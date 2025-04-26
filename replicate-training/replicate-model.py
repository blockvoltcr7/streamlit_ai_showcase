import replicate
 
 
model = replicate.models.create(
    owner="SamiSabirIdrissi",
    name="rflkt-v1",
    visibility="private",  # or "private" if you prefer
    hardware="gpu-t4",  # Replicate will override this for fine-tuned models
    description="A fine-tuned FLUX.1 model"
)
 
print(f"Model created: {model.name}")
print(f"Model URL: https://replicate.com/{model.owner}/{model.name}")


# Now use this model as the destination for your training
training = replicate.trainings.create(
    version="ostris/flux-dev-lora-trainer:4ffd32160efd92e956d39c5338a9b8fbafca58e03f791f6d8011f3e20e8ea6fa",
    input={
        "input_images": open("../replicate-training/training-image-set-rrflkt.zip", "rb"),
        "steps": 1000
    },
    destination=f"{model.owner}/{model.name}"
)
 
print(f"Training started: {training.status}")
print(f"Training URL: https://replicate.com/p/{training.id}")

 
# output = replicate.run(
#     "yourusername/flux-your-model-name:version_id",
#     input={
#         "prompt": "A portrait photo of a space station, bad 70s food",
#         "num_inference_steps": 28,
#         "guidance_scale": 7.5,
#         "model": "dev",
#     }
# )
 
# print(f"Generated image URL: {output}")