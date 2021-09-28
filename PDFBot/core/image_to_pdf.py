from PIL import Image


async def images_to_pdf(paths, output):
    image_list = []
    for path in paths:
        image = Image.open(path)
        pic = image.convert('RGB')
        image_list.append(pic)
    first = image_list[0]
    image_list.pop(0)
    first.save(output, resolution=100.0, save_all=True, append_images=image_list)
