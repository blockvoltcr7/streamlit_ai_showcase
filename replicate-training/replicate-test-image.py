import replicate

output = replicate.run(
    "black-forest-labs/flux-1.1-pro-ultra",
    input={
        "raw": False,
        "prompt": "Create a high-contrast black-and-white illustration of a solitary warrior in a dark flowing cloak, center-mass on a jagged snow-dusted peak, back turned, sword hilt catching faint diffused light; a low-angle wide shot reveals the desolate hush of white rock against a velvet sky speckled with sparse stars, vast negative space above. Bold silhouettes, sharp highlights, cracked textures, controlled grays, film grain and dust evoke isolation and determination in a noir–sumi-e, distressed-print style—cinematic, raw, timeless. -no signature --no watermark --no text",
        "aspect_ratio": "9:16",
        "output_format": "jpg",
        "safety_tolerance": 2,
        "image_prompt_strength": 0.1
    }
)
print(output)