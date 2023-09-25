import supervisely as sly

# authenticate with your personal API token
api = sly.Api.from_env()

# create project and dataset
##project = api.project.create(workspace_id=123, name="demo project")
dataset = api.dataset.create(project.id, "dataset-01")

# upload data
#image_info = api.image.upload_path(dataset.id, "img.png", "/Users/max/img.png")
#api.annotation.upload_path(image_info.id, "/Users/max/ann.json")

# download data
#img = api.image.download_np(image_info.id)
##ann = api.annotation.download_json(image_info.id)