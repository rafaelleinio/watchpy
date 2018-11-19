import sys
import cv2
import imutils
import matplotlib.pyplot as plt
import glob


def open_image(image_path):
    return cv2.imread(image_path)


def plot_image(image):
    plt.axis("off")
    plt.imshow(image)
    plt.figure()
    plt.show()


def augmentation_rotate_x4(image):
    return [image,
            imutils.rotate_bound(image,90),
            imutils.rotate_bound(image,180),
            imutils.rotate_bound(image,270)]


def augmentation_flip(image):
    return [image, cv2.flip(image,1)]


def get_dataset(dataset_path):
    types = (dataset_path + '*.jpg',
             dataset_path + '*.jpeg',
             dataset_path + '*.png') # the tuple of file types
    image_files = []
    for files in types:
        image_files.extend(glob.glob(files))
    return image_files


def data_augmentation(image_files):
    augmentated_set = []
    for image_file in image_files:
        print(image_file)
        image = open_image(image_file)
        original, flipped = augmentation_flip(image)
        augmentated_set.extend(augmentation_rotate_x4(original))
        augmentated_set.extend(augmentation_rotate_x4(flipped))
    return augmentated_set


def resize_image(image, max_height, max_width):
    height, width = image.shape[:2]
    # only shrink if img is bigger than required
    if max_height < height or max_width < width:
        # get scaling factor
        scaling_factor = max_height / float(height)
        if max_width/float(width) < scaling_factor:
            scaling_factor = max_width / float(width)
        # resize image
        return cv2.resize(image, None, fx=scaling_factor, fy=scaling_factor, interpolation=cv2.INTER_AREA)


def save_images(output_folder_path, images):
    for i, image in enumerate(images):
        cv2.imwrite(output_folder_path + str(i) + '.png',image)


def create_augmentaded_set(input_set_path, output_set_path):
    image_files = get_dataset(input_set_path)
    augmentated_set = data_augmentation(image_files)
    save_images(output_set_path, augmentated_set)
    

def create_resized_set(input_set_path, output_set_path, max_size):
    image_files = get_dataset(input_set_path)
    resized_set = []
    for image_file in image_files:
        print(image_file)
        resized_set.append(resize_image(open_image(image_file), max_size, max_size))
    save_images(output_set_path, resized_set)

print("Starting resize")
#create_resized_set('/home/rafael/Documents/tcc/dcscn-super-resolution-master/data/images/', '/home/rafael/Documents/tcc/dcscn-super-resolution-master/data/images_resized/', 384)
print("Starting Augmentation")
create_augmentaded_set('/home/rafael/Documents/tcc/dcscn-super-resolution-master/data/images_resized/', '/home/rafael/Documents/tcc/dcscn-super-resolution-master/data/images_aug/')
