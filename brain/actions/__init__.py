import os
import re
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    AutoModelForQuestionAnswering,
    AutoModelForSeq2SeqLM,
    GPTNeoForCausalLM,
    GPT2Tokenizer,
)

class ModelHandler:
  _instance = None

  def __new__(cls):
    if cls._instance is None:
      cls._instance = super().__new__(cls)
      cls._instance.initialize_models()
    return cls._instance

  def initialize_models(self):
    self.chat_model_name = "gpt-neo-1.3B"
    self.qa_model_name = "roberta-base-squad2"
    self.summarization_model_name = "bart-large-cnn"
    self.generation_model_name = "gpt2-large"
    self.paraphrase_model_name = "pegasus_paraphrase"
    self.parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    self.models_dir = os.path.join(self.parent_dir, "pretrained_models")

    self.chat_model_path = os.path.join(self.models_dir, self.chat_model_name, "model")
    self.chat_tokenizer_path = os.path.join(self.models_dir, self.chat_model_name, "tokenizer")
    self.qa_model_path = os.path.join(self.models_dir, self.qa_model_name, "model")
    self.qa_tokenizer_path = os.path.join(self.models_dir, self.qa_model_name, "tokenizer")
    self.summarization_model_path = os.path.join(self.models_dir, self.summarization_model_name, "model")
    self.summarization_tokenizer_path = os.path.join(self.models_dir, self.summarization_model_name, "tokenizer")
    self.generation_model_path = os.path.join(self.models_dir, self.generation_model_name, "model")
    self.generation_tokenizer_path = os.path.join(self.models_dir, self.generation_model_name, "tokenizer")
    self.paraphrase_model_path = os.path.join(self.models_dir, self.paraphrase_model_name, "model")
    self.paraphrase_tokenizer_path = os.path.join(self.models_dir, self.paraphrase_model_name, "tokenizer")

    self.download_and_save_model(self.chat_model_name, self.chat_model_path, self.chat_tokenizer_path, GPT2Tokenizer, GPTNeoForCausalLM, "EleutherAI/")
    self.download_and_save_model(self.qa_model_name, self.qa_model_path, self.qa_tokenizer_path, AutoTokenizer, AutoModelForQuestionAnswering, "deepset/")
    self.download_and_save_model(self.summarization_model_name, self.summarization_model_path, self.summarization_tokenizer_path, AutoTokenizer, AutoModelForSeq2SeqLM, "facebook/")
    self.download_and_save_model(self.generation_model_name, self.generation_model_path, self.generation_tokenizer_path, AutoTokenizer, AutoModelForCausalLM, "")
    self.download_and_save_model(self.paraphrase_model_name, self.paraphrase_model_path, self.paraphrase_tokenizer_path, AutoTokenizer, AutoModelForSeq2SeqLM, "tuner007/")

    self.load_model(self.chat_tokenizer_path, self.chat_model_path, GPT2Tokenizer, GPTNeoForCausalLM, "chat")
    self.load_model(self.qa_tokenizer_path, self.qa_model_path, AutoTokenizer, AutoModelForQuestionAnswering, "qa")
    self.load_model(self.summarization_tokenizer_path, self.summarization_model_path, AutoTokenizer, AutoModelForSeq2SeqLM, "summarization")
    self.load_model(self.generation_tokenizer_path, self.generation_model_path, AutoTokenizer, AutoModelForCausalLM, "generation")
    self.load_model(self.paraphrase_tokenizer_path, self.paraphrase_model_path, AutoTokenizer, AutoModelForSeq2SeqLM, "paraphrase")

  def download_and_save_model(self, model_name, model_path, tokenizer_path, tokenizer_class, model_class, model_author):
    if not os.path.isdir(tokenizer_path):
      print(f"Getting {model_name} Tokenizer")
      os.makedirs(tokenizer_path, exist_ok=True)
      tokenizer = tokenizer_class.from_pretrained(f"{model_author}{model_name}")
      tokenizer.save_pretrained(tokenizer_path)

    if not os.path.isdir(model_path):
      print(f"Getting {model_name} Model")
      os.makedirs(model_path, exist_ok=True)
      model = model_class.from_pretrained(f"{model_author}{model_name}")
      model.save_pretrained(model_path)

  def load_model(self, tokenizer_path, model_path, tokenizer_class, model_class, model_description):
    print(f"Loading {model_description} Tokenizer")
    tokenizer = tokenizer_class.from_pretrained(tokenizer_path)
    print(f"Loading {model_description} Model")
    model = model_class.from_pretrained(model_path)

    if model_description.lower() == "summarization":
        setattr(self, "summarization_tokenizer", tokenizer)
        setattr(self, "summarization_model", model)
    elif model_description.lower() == "chat":
        setattr(self, "chat_tokenizer", tokenizer)
        setattr(self, "chat_model", model)
    elif model_description.lower() == "qa":
        setattr(self, "qa_tokenizer", tokenizer)
        setattr(self, "qa_model", model)
    elif model_description.lower() == "generation":
        setattr(self, "generation_tokenizer", tokenizer)
        setattr(self, "generation_model", model)
    elif model_description.lower() == "paraphrase":
        setattr(self, "paraphrase_tokenizer", tokenizer)
        setattr(self, "paraphrase_model", model)

  def generate_chat_response(self, user_input: str, username: str) -> str:
    input_ids = self.chat_tokenizer.encode(user_input, return_tensors="pt")
    attention_mask = torch.ones_like(input_ids)

    max_length = input_ids.size(1) + 50

    output = self.chat_model.generate(
      input_ids=input_ids,
      attention_mask=attention_mask,
      do_sample=True,
      temperature=0.9,
      max_length=max_length,
      num_return_sequences=1,
      pad_token_id=self.chat_tokenizer.eos_token_id
    )

    generated_response = self.chat_tokenizer.decode(output[0], skip_special_tokens=True)

    # Compare the generated response with the input
    input_tokens = user_input.split()
    generated_tokens = generated_response.split()
    num_common_tokens = 0

    for i in range(min(len(input_tokens), len(generated_tokens))):
      if input_tokens[i] == generated_tokens[i]:
        num_common_tokens += 1
      else:
        break

    # Remove repeating words at the beginning
    generated_response = " ".join(generated_tokens[num_common_tokens:])

    # Remove "Nick:" and everything following it
    generated_response = generated_response.split(f"{username}:", 1)[0].strip()

    return generated_response
  
  def generate_qa_response(self, question: str, context: str) -> str:
    inputs = self.qa_tokenizer.encode_plus(question, context, add_special_tokens=True, return_tensors="pt")
    input_ids = inputs["input_ids"].tolist()[0]

    # Perform the question answering
    outputs = self.qa_model(**inputs)
    answer_start_scores = outputs.start_logits
    answer_end_scores = outputs.end_logits

    # Find the start and end positions with the highest scores
    answer_start = torch.argmax(answer_start_scores)
    answer_end = torch.argmax(answer_end_scores) + 1

    # Get the final answer by decoding the tokens
    answer = self.qa_tokenizer.convert_tokens_to_string(self.qa_tokenizer.convert_ids_to_tokens(input_ids[answer_start:answer_end]))

    return answer
  
  def generate_summarization_response(self, text: str) -> str:
    inputs = self.summarization_tokenizer.encode(text, return_tensors="pt", truncation=True)
    max_length = inputs.size(1)

    # Generate summary
    summary_ids = self.summarization_model.generate(inputs, max_length=max_length, num_beams=4, early_stopping=False)
    summary = self.summarization_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    
    return summary
  
  def generate_generation_response(self, goal: str, start_text: str) -> str:
    # Combine the goal and start text
    input_text = f"Goal: {goal}\n\nStart: {start_text}"

    input_ids = self.generation_tokenizer.encode(input_text, return_tensors="pt")
    attention_mask = torch.ones_like(input_ids)  # Create attention mask

    max_length = input_ids.size(1) + 200

    # Generate text using the model
    output = self.generation_model.generate(
      input_ids=input_ids,
      attention_mask=attention_mask,  
      pad_token_id=self.generation_tokenizer.eos_token_id,  
      max_length=max_length,
      num_return_sequences=1,
      early_stopping=True,
      temperature=0.5,      
      top_k=10,             
      num_beams=5,
      no_repeat_ngram_size=2  
    )

    # Decode the generated output
    generated_text = self.generation_tokenizer.decode(output[0], skip_special_tokens=True)
    return generated_text
  
  def generate_paraphrase_response(self, text: str) -> str:
    sentences = re.split(r'[.!?]', text)  # Split text into sentences using punctuation marks
    paraphrases = []

    for sentence in sentences:
      sentence = sentence.strip()  # Remove leading/trailing whitespace
      if sentence:  # Check if the sentence is not empty
        inputs = self.paraphrase_tokenizer.batch_encode_plus(
          [sentence],
          truncation=True,
          padding='longest',
          max_length=60,
          return_tensors="pt"
        )

        outputs = self.paraphrase_model.generate(
          input_ids=inputs['input_ids'],
          attention_mask=inputs['attention_mask'],
          max_length=60,
          num_beams=4,
          early_stopping=False
        )

        paraphrased_text = self.paraphrase_tokenizer.batch_decode(outputs, skip_special_tokens=True)
        paraphrases.append(paraphrased_text[0])

    reconstructed_text = ' '.join(paraphrases)
    return reconstructed_text