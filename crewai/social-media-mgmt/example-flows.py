#!/usr/bin/env python
from dotenv import load_dotenv
from litellm import completion
from pydantic import BaseModel

try:
    from crewai.flow.flow import Flow, listen, start
except ImportError as e:
    print(
        f"Import error: {e}. Please ensure the 'crewai' package is installed and accessible."
    )


class SocialMediaState(BaseModel):
    brand_tone: str = ""
    caption: str = ""
    hashtags: str = ""


class SocialMediaFlow(Flow[SocialMediaState]):
    model = "gpt-4o-mini"

    @start()
    def analyze_brand_tone(self):
        print("Starting brand tone analysis")

        response = completion(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": "Analyze the tone for a wellness brand. Return 3 key tone characteristics.",
                },
            ],
        )

        self.state.brand_tone = response["choices"][0]["message"]["content"]
        print(f"Brand Tone Analysis: {self.state.brand_tone}")
        return self.state.brand_tone

    @listen(analyze_brand_tone)
    def generate_caption(self, brand_tone):
        response = completion(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": f"Create an Instagram caption following this brand tone: {brand_tone}",
                },
            ],
        )

        self.state.caption = response["choices"][0]["message"]["content"]
        return self.state.caption

    @listen(generate_caption)
    def generate_hashtags(self, caption):
        response = completion(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": f"Generate 5 relevant hashtags for this Instagram caption: {caption}",
                },
            ],
        )

        self.state.hashtags = response["choices"][0]["message"]["content"]
        return self.state.hashtags


def kickoff():
    # Initialize and run flow
    social_media_flow = SocialMediaFlow()
    result = social_media_flow.kickoff()

    # Print results
    print("\n=== Final Results ===")
    print(f"Brand Tone: {result.state.brand_tone}")
    print(f"Caption: {result.state.caption}")
    print(f"Hashtags: {result.state.hashtags}")


if __name__ == "__main__":
    load_dotenv()
    kickoff()
