from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch


class EmbeddingGenerator:
    
    def __init__(self):
        model_name_or_path="sentence-transformers/all-MiniLM-L6-v2"
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name_or_path).eval()

    def generate_embeddings(self,text:str)->list[float]:
      inputs=self.tokenizer(text,padding=True,truncation=True,max_length=512 ,return_tensors='pt')
      with torch.no_grad():
          embeddings=self.model(**inputs).last_hidden_state.mean(dim=-1).squeeze().tolist() 
        
      return embeddings
      
      
if __name__=="__main__":
   generator_model_instance_ = EmbeddingGenerator()