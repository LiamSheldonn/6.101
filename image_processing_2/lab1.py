#!/usr/bin/env python3

"""
6.101 Lab 1:
Image Processing
"""

import math

from PIL import Image

# NO ADDITIONAL IMPORTS ALLOWED!


def get_pixel(image, row, col):
    """
    Returns pixel at (row,col) in image.
    """
    if row >= image["height"] or row < 0 or col >= image["width"] or col < 0:
        raise IndexError
    index = row*image["width"]+col
    return image["pixels"][index]


def set_pixel(image, row, col, color):
    """
    Sets the pixel at (row,col) in image to color.
    """
    num_pixels = len(image["pixels"])
    if row >= image["height"] or row < 0 or col >= image["width"] or col < 0:
        raise IndexError

    index = (row)*image["width"]+col
    if index >= num_pixels:
        image["pixels"] += [0]*(index+1-num_pixels)
    image["pixels"][index] = color


def apply_per_pixel(image, func):
    """
    Return a new array where each cell is the result of func
    applied to the corresponding cell in image.
    """
    result = {
        "height": image["height"],
        "width": image["width"],
        "pixels": [],
    }
    for col in range(image["width"]):
        for row in range(image["height"]):
            color = get_pixel(image, row, col)
            new_color = func(color)
            set_pixel(result, row, col, new_color)
    return result


def inverted(image):
    return apply_per_pixel(image, lambda color: 255-color)


# HELPER FUNCTIONS

def correlate(image, kernel, boundary_behavior):
    """
    Compute the result of correlating the given image with the given kernel.
    `boundary_behavior` will one of the strings "zero", "extend", or "wrap",
    and this function will treat out-of-bounds pixels as having the value zero,
    the value of the nearest edge, or the value wrapped around the other edge
    of the image, respectively.

    if boundary_behavior is not one of "zero", "extend", or "wrap", return
    None.

    Otherwise, the output of this function should have the same form as a 6.101
    image (a dictionary with "height", "width", and "pixels" keys), but its
    pixel values do not necessarily need to be in the range [0,255], nor do
    they need to be integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    First, this iterates through all cells in the image, in row-order form. 
    For each cell, it sums up the cell-wise multiplications of the kernel.

    To do the cell-wise multiplication, it first shifts the kernel indices,
    such that indices (0,0) is the center cell of the kernel. Then, it
    iterates over the kernel indices, multiplying cell (i,j) (where i and j 
    are the new indices) in the kernel by cell (n+i,m+j) (where n and m are the 
    coordinates of the current working cell in the image). Then it sums up all 
    these multiplications.

    Returns the new correlated image, in dictionary form.

    """

    image_rows = image["height"]
    image_cols = image["width"]
    kernel_rows = kernel["height"]
    kernel_cols = kernel["width"]

    if kernel_rows != kernel_cols:
        raise ValueError("Kernel must be square.")
    if kernel_rows%2 == 0 or kernel_cols%2 == 0:
        raise ValueError("Kernel must have odd dimensions.")

    new = {
        "height": image_rows,
        "width": image_cols,
        "pixels": [0]*image_cols*image_rows,
    }

    for ir in range(image_rows):
        for ic in range(image_cols):
            current_sum = 0
            for kr in range(kernel_rows):
                shifted_kr = kr - kernel_rows//2
                for kc in range(kernel_cols):

                    shifted_kc = kc - kernel_cols//2

                    shifted_ir = ir + shifted_kr
                    shifted_ic = ic + shifted_kc
                    if 0<shifted_ir<image_rows and 0<shifted_ic<image_cols:
                        image_pixel = get_pixel(image,shifted_ir,shifted_ic)
                        kernel_pixel = get_pixel(kernel, kr,kc)
                        current_sum += image_pixel*kernel_pixel
                    elif boundary_behavior == "wrap":
                        if shifted_ir < 0:
                            shifted_ir += image_rows
                        if shifted_ic < 0:
                            shifted_ic += image_cols
                        if shifted_ir >= image_rows:
                            shifted_ir = shifted_ir%image_rows
                        if shifted_ic >= image_cols:
                            shifted_ic = shifted_ic%image_cols
                        image_pixel = get_pixel(image,shifted_ir,shifted_ic)
                        kernel_pixel = get_pixel(kernel, kr,kc)
                        current_sum += image_pixel*kernel_pixel
                    elif boundary_behavior == "extend":
                        shifted_ir = min(max(shifted_ir,0),image_rows-1)
                        shifted_ic = min(max(shifted_ic,0),image_cols-1)
                        image_pixel = get_pixel(image,shifted_ir,shifted_ic)
                        kernel_pixel = get_pixel(kernel, kr,kc)
                        current_sum += image_pixel*kernel_pixel
                    elif boundary_behavior != "zero":
                        return None
            set_pixel(new, ir,ic,current_sum)
    return new

def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the "pixels" list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python"s `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """

    new = []

    for pixel in image["pixels"]:

        if pixel > 255:
            new.append(255)
        elif pixel < 0:
            new.append(0)
        else:
            new.append(round(pixel))

    image["pixels"] = new


# FILTERS

def create_kernel(kernel_size, kernel_type):
    """
    Helper function that creates kernels of dimensions *kernel_size* by 
    *kernel_size* depending on the operation you"re using for correlation.

    Two types, "blur" and "sharpen". 
    Blur creates an n by n kernel where each cell is 1/(n^2).
    Sharpen creates an n by n kernel that is equal to 2*I-B,
    where I is the identity kernel (all zeros except for 1 in 
    the middle), and B is the blur kernel.

    Returns a kernel.
    """
    new = {
        "width": kernel_size,
        "height": kernel_size,
        "pixels": [],
    }
    if kernel_type == "blur":
        new["pixels"] = [1/(kernel_size**2)]*(kernel_size**2)
    if kernel_type == "sharpen":
        new["pixels"] = [-1/(kernel_size**2)]*(kernel_size**2)
        set_pixel(new,kernel_size//2,kernel_size//2,2-1/(kernel_size**2))
    return new



def blurred(image, kernel_size, kernel_behavior="extend"):
    """
    Return a new image representing the result of applying a box blur (with the
    given kernel size) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    kernel = create_kernel(kernel_size, "blur")
    correlated_im = correlate(image, kernel, kernel_behavior)
    round_and_clip_image(correlated_im)
    return correlated_im
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)

    # then compute the correlation of the input image with that kernel

    # and, finally, make sure that the output is a valid image (using the
    # helper function from above) before returning it.

def sharpened(image,n, kernel_behavior="extend"):
    """
    Sharpens *image* by applying the sharpen kernel defined
    in *create_kernel*
    """
    kernel = create_kernel(n,"sharpen")
    correlated_im = correlate(image, kernel, kernel_behavior)
    round_and_clip_image(correlated_im)
    return correlated_im

def edges(image):
    """
    Performs edge detection using the Sobel operator.

    First correlates each input with k_1 and k_2, as defined below.

    Then creates a new array where each cell is the square root of 
    the squares of each corresponding cell in the kernels.

    Finally, rounds and clips all values, and returns the new array. 
    """
    k_1 = {
        "width":3,
        "height":3,
        "pixels":[-1,-2,-1,0,0,0,1,2,1]
    }

    k_2 = {
        "width":3,
        "height":3,
        "pixels":[-1,0,1,-2,0,2,-1,0,1]
    }

    o_1 = correlate(image,k_1,"extend")
    o_2 = correlate(image,k_2,"extend")

    o_final = {
        "width":image["width"],
        "height":image["height"],
        "pixels":[]
    }
    for i,x in enumerate(o_1["pixels"]):
        o_final["pixels"].append(round(math.sqrt(x**2+o_2["pixels"][i]**2)))

    round_and_clip_image(o_final)
    return o_final


# HELPER FUNCTIONS FOR LOADING AND SAVING IMAGES

def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns a dictionary
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image("test_images/cat.png")
    """
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith("RGB"):
            pixels = [round(.299 * p[0] + .587 * p[1] + .114 * p[2])
                      for p in img_data]
        elif img.mode == "LA":
            pixels = [p[0] for p in img_data]
        elif img.mode == "L":
            pixels = list(img_data)
        else:
            raise ValueError(f"Unsupported image mode: {img.mode}")
        width, height = img.size
        return {"height": height, "width": width, "pixels": pixels}


def save_greyscale_image(image, filename, mode="PNG"):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the "mode" parameter.
    """
    out = Image.new(mode="L", size=(image["width"], image["height"]))
    out.putdata(image["pixels"])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == "__main__":
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    # im = load_greyscale_image("test_images/bluegill.png")
    # save_greyscale_image(inverted(im), "bluegill_inverted.png")

    # imtest = {
    #     "height": 3,
    #     "width": 3,
    #     "pixels": [80,53,99,129,127,148,175,174,193],
    # }

    # kertest = {
    #     "height": 3,
    #     "width": 3,
    #     "pixels": [0.00,-0.07,0.00,-0.45,1.20,-0.25,0.00,-0.12,0.00],
    # }
    # print(correlate(imtest,kertest,"zero"))

    # kertest = {
    #     "height": 13,
    #     "width": 13,
    #     "pixels": [],
    # }
    # set_pixel(kertest, 12,12,0)
    # set_pixel(kertest, 2,0,1)

    # im = load_greyscale_image("test_images/pigbird.png")
    # zero_correlate = correlate(im,kertest,"zero")
    # wrap_correlate = correlate(im,kertest,"wrap")
    # extend_correlate = correlate(im,kertest,"extend")

    # save_greyscale_image(zero_correlate, "pigbird_correlate_zero.png")
    # save_greyscale_image(wrap_correlate, "pigbird_correlate_wrap.png")
    # save_greyscale_image(extend_correlate, "pigbird_correlate_extend.png")

    # test ={
    #     "pixels":[1.2,1.3,1.4,256,257,-1,-1.2]
    # }

    # print(test)
    # round_and_clip_image(test)
    # print(test)

    # im = load_greyscale_image("test_images/cat.png")
    # save_greyscale_image(blurred(im, 13), "cat_blur.png")
    # save_greyscale_image(blurred(im, 13, "zero"), "cat_blur_zero.png")
    # save_greyscale_image(blurred(im, 13, "wrap"), "cat_blur_wrap.png")

    # im = load_greyscale_image("test_images/python.png")
    # save_greyscale_image(sharpened(im,11),"python_sharpened.png")

    im = load_greyscale_image("test_images/construct.png")
    save_greyscale_image(edges(im),"edged_construct.png")




