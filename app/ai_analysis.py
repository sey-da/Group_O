import base64
import ollama
import yaml
import os
import csv
import datetime
from pathlib import Path
import pandas as pd

class AIAnalysis:
    def __init__(self, config_path="models.yaml"):
        """Initialize the handler by loading configurations from the YAML file."""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

    def ensure_model(self, model_name: str) -> None:
        """
        Check if a model exists locally in ollama.
        If it does not exist, pull it automatically.
        """
        try:
            available_models = [m.model for m in ollama.list().models]
            if model_name not in available_models:
                print(f"Model '{model_name}' not found locally. Pulling now...")
                ollama.pull(model_name)
                print(f"Model '{model_name}' is ready.")
        except Exception as e:
            print(f"Error checking/pulling model: {e}")

    def describe_image(self, image_path: str) -> str:
        """
        Converts image to base64 and uses a vision model to generate a description.
        """
        model = self.config['vision_model']['name']
        prompt = self.config['vision_model']['prompt']
        
        self.ensure_model(model)

        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        response = ollama.chat(
            model=model,
            messages=[{
                "role": "user",
                "content": prompt,
                "images": [image_data],
            }],
        )
        return response["message"]["content"]

    def assess_environmental_risk(self, description: str) -> dict:
        """
        Analyses the description text to detect environmental risks.
        Returns a dictionary with the full response and a boolean flag.
        """
        model = self.config['analysis_model']['name']
        prompt_template = self.config['analysis_model']['prompt']
        
        self.ensure_model(model)

        # Inject description into the template
        full_prompt = f"{prompt_template}\n\nDescription: {description}"

        response = ollama.chat(
            model=model,
            messages=[{
                "role": "user",
                "content": full_prompt,
            }],
        )

        response_text = response["message"]["content"]
        
        # Risk detection logic based on keywords
        risk_keywords = ["yes", "danger", "risk", "threat", "deforest", "degrad", "concern", "harmful"]
        is_at_risk = any(kw in response_text.lower() for kw in risk_keywords)

        return {
            "response": response_text,
            "is_at_risk": is_at_risk
        }

    def log_to_database(self, latitude, longitude, zoom, image_description, text_response, danger):
        db_dir = Path("database")
        db_dir.mkdir(exist_ok=True)
        csv_path = db_dir / "images.csv"

        new_row = pd.DataFrame([{
            "timestamp": datetime.datetime.now().isoformat(),
            "latitude": latitude,
            "longitude": longitude,
            "zoom": zoom,
            "image_description": image_description,
            "image_prompt": self.config["vision_model"]["prompt"].split(".")[0].strip(),
            "image_model": self.config["vision_model"]["name"],
             "text_description": text_response,
            "text_prompt": self.config["analysis_model"]["prompt"].split("\n")[0].strip(),
            "text_model": self.config["analysis_model"]["name"],
            "danger": "Y" if danger else "N"
        }])

        if csv_path.exists():
            new_row.to_csv(csv_path, mode="a", header=False, index=False)
        else:
            new_row.to_csv(csv_path, index=False)

    def check_database(self, latitude: float, longitude: float, zoom: int):
        """
        Check if the current coordinates and zoom already exist in the database.
        Returns the existing row as a dict if found, or None if not found.
        """
        csv_path = Path("database") / "images.csv"
        
        if not csv_path.exists():
            return None
        
        df = pd.read_csv(csv_path)
        match = df[
            (df["latitude"] == latitude) &
            (df["longitude"] == longitude) &
            (df["zoom"] == zoom)
        ]
        
        if not match.empty:
            return match.iloc[-1].to_dict()  # return most recent match
        return None