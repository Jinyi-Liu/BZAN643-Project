from transformers import AutoTokenizer, AutoModelForSequenceClassification
from datasets import Dataset
import pandas as pd
import pickle
tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")

from datasets import load_dataset

# Load the dataset in pickle format
with open('data/train_data.pickle', 'rb') as f:
    data = pickle.load(f)
# Rename the columns to text and label
data.columns = ['text', 'label']
data.label = data.label.replace({'gamesale': 1, 'gameswap': 0})

# Split the data into train and test
train_data = data[:int(len(data)*0.8)]
test_data = data[int(len(data)*0.8):]

# Load the dataset by dataframe
train_dataset = Dataset.from_pandas(train_data, split="train")
test_dataset = Dataset.from_pandas(test_data, split="test")

# Tokenize the data
train_dataset = train_dataset.map(lambda examples: tokenizer(examples["text"], truncation=True, padding="max_length"), batched=True)
test_dataset = test_dataset.map(lambda examples: tokenizer(examples["text"], truncation=True, padding="max_length"), batched=True)

# Get the model
model = AutoModelForSequenceClassification.from_pretrained("bert-base-cased", num_labels=2)

# Train the model
from transformers import Trainer, TrainingArguments

training_args = TrainingArguments(
    output_dir='./results',          # output directory
    num_train_epochs=3,              # total # of training epochs
    per_device_train_batch_size=16,  # batch size per device during training
    per_device_eval_batch_size=64,   # batch size for evaluation
    warmup_steps=500,                # number of warmup steps for learning rate scheduler
    weight_decay=0.01,               # strength of weight decay
    logging_dir='./logs',            # directory for storing logs
    logging_steps=10,
)

trainer = Trainer(
    model=model,                         # the instantiated 🤗 Transformers model to be trained
    args=training_args,                  # training arguments, defined above
    train_dataset=train_dataset,         # training dataset
    eval_dataset=test_dataset,           # evaluation dataset
)

trainer.train()

# Save the model
trainer.save_model("model")

# Evaluate the model
trainer.evaluate()

# Predict the model
trainer.predict(test_dataset)

# Get the prediction
pred = trainer.predict(test_dataset)
pred = pred.predictions.argmax(axis=-1)

# Get the accuracy
from sklearn.metrics import accuracy_score
accuracy_score(test_data['label'], pred)

# Get the confusion matrix
from sklearn.metrics import confusion_matrix
confusion_matrix(test_data['label'], pred)

# Get the classification report
from sklearn.metrics import classification_report
print(classification_report(test_data['label'], pred))

# Get the ROC curve
from sklearn.metrics import roc_curve
import matplotlib.pyplot as plt
import seaborn as sns

# Get the probability
pred_prob = trainer.predict(test_dataset)
pred_prob = pred_prob.predictions[:, 1]

# Get the fpr, tpr, and threshold
fpr, tpr, threshold = roc_curve(test_data['label'], pred_prob)

# Plot the ROC curve
plt.figure(figsize=(10, 10))
plt.plot(fpr, tpr, label='ROC curve')
plt.plot([0, 1], [0, 1], 'k--', label='Random guess')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC curve')
plt.legend()
plt.show()

# Clear the GPU memory
import torch
torch.cuda.empty_cache()


# Use the model to predict another text
text = "I want to sell my game"
encoded_input = tokenizer(text, padding=True, truncation=True, return_tensors="pt").to('cuda')
output = model(**encoded_input)
output = output.logits.argmax(axis=-1)
print(output)

