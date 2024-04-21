#!/usr/bin/env python3

"""
6.101 Lab 2:
Image Processing 2
"""

# NO ADDITIONAL IMPORTS!
# (except in the last part of the lab; see the lab writeup for details)
import math
from PIL import Image

#Lab 1 Functions

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


# VARIOUS FILTERS

def grey_from_color(image,index):
    pix = image["pixels"]
    return [pix[i][index] for i in range(len(pix))]


def color_filter_from_greyscale_filter(filt):
    """
    Given a filter that takes a greyscale image as input and produces a
    greyscale image as output, returns a function that takes a color image as
    input and produces the filtered color image.
    """
    def color_filter(im):
        #im_pix = im["pixels"]
        # (r,g,b) = (grey_from_color(im_pix,i) for i in range(3))

        (red,green,blue) = (
            {
            "width":im["width"],
            "height":im["height"],
            "pixels":grey_from_color(im,i)
            } for i in range(3)
        )
        filtered_r = filt(red)["pixels"]
        filtered_g = filt(green)["pixels"]
        filtered_b = filt(blue)["pixels"]

        out = list(zip(filtered_r,filtered_g,filtered_b))
        return {
            "width":im["width"],
            "height":im["height"],
            "pixels":out
        }

    return color_filter



def make_blur_filter(kernel_size):
    def spec_blur_filt(im):
        return blurred(im,kernel_size)
    return spec_blur_filt

def make_sharpen_filter(kernel_size):
    def spec_sharp_filt(im):
        return sharpened(im,kernel_size)
    return spec_sharp_filt


def filter_cascade(filters):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    """
    def cascade(im):
        new = filters[0](im)
        for filt in filters[1:]:
            new = filt(new)
        return new
    return cascade


# SEAM CARVING

# Main Seam Carving Implementation


def seam_carving(image, ncols):
    """
    Starting from the given image, use the seam carving technique to remove
    ncols (an integer) columns from the image. Returns a new image.
    """
    cem_func = filter_cascade([
        greyscale_image_from_color_image,
        compute_energy,
        cumulative_energy_map])
    out = {
        "width":image["width"],
        "height":image["height"],
        "pixels":image["pixels"][:]
    }
    for i in range(ncols):
        cem = cem_func(out)
        min_seam = minimum_energy_seam(cem)
        out = image_without_seam(out,min_seam)
        print(f"{(i+1)*100/ncols}%")
    return out

# Optional Helper Functions for Seam Carving


def greyscale_image_from_color_image(image):
    """
    Given a color image, computes and returns a corresponding greyscale image.

    Returns a greyscale image (represented as a dictionary).
    """
    pixels = image["pixels"]

    return {
        "width":image["width"],
        "height":image["height"],
        "pixels":[
            round(0.299*pixels[i][0]+0.587*pixels[i][1]+0.114*pixels[i][2])
            for i in range(len(pixels))
        ]
    }


def compute_energy(grey):
    """
    Given a greyscale image, computes a measure of "energy", in our case using
    the edges function from last week.

    Returns a greyscale image (represented as a dictionary).
    """
    assert isinstance(grey, dict)
    assert isinstance(grey["pixels"][0],int)

    return edges(grey)

def min_energy_pixel(image, row, col, return_type = "value"):
    """
    Helper function to find the minimum pixel of the 3 pixels
    above pixel (*row*,*col*).

    Returns either the index, as a tuple of (row,col), 
    or the actual value, depending on *return_type*

    """

    all_adjacent_indices = [(row-1,col-1),(row-1,col),(row-1,col+1)]
    actual_adjacent_pixels = []
    actual_adjacent_indices = []

    for index in all_adjacent_indices:
        if index[1] >= 0 and index[1] < image["width"]:
            current_pixel_to_add = get_pixel(image, *index)
            actual_adjacent_indices.append(index)
            actual_adjacent_pixels.append(current_pixel_to_add)

    min_energy = min(actual_adjacent_pixels)

    index_of_min_energy = actual_adjacent_indices[
        actual_adjacent_pixels.index(min_energy)
        ]

    if return_type == "value":
        return min_energy
    elif return_type == "index":
        return index_of_min_energy

def cumulative_energy_map(energy):
    """
    Given a measure of energy (e.g., the output of the compute_energy
    function), computes a "cumulative energy map" as described in the lab 2
    writeup.

    Returns a dictionary with "height", "width", and "pixels" keys (but where
    the values in the "pixels" array may not necessarily be in the range [0,
    255].
    """

    energy_pixels = energy["pixels"]
    cum_map = {
        "width":energy["width"],
        "height":energy["height"],
        "pixels":energy_pixels[:]
    }
    for ir in range(cum_map["height"]):
        for ic in range(cum_map["width"]):
            if ir != 0:
                min_adj_energy_val = min_energy_pixel(cum_map, ir,ic)
                cum_val = min_adj_energy_val+get_pixel(cum_map,ir,ic)
                set_pixel(cum_map,ir,ic,cum_val)
    return cum_map


def minimum_energy_seam(cem):
    """
    Given a cumulative energy map, returns a list of the indices into the
    "pixels" list that correspond to pixels contained in the minimum-energy
    seam (computed as described in the lab 2 writeup).
    """
    removed_pixels = []
    c_w = cem["width"]
    c_h = cem["height"]
    cem_pixels = cem["pixels"]
    last_row = cem_pixels[c_w*(c_h-1):c_w*c_h]
    min_last_pixel = min(last_row)
    last_index = cem_pixels[c_w*(c_h-1):c_w*c_h].index(min_last_pixel)
    removed_pixels.append((c_h-1,last_index))

    for _ in range(c_h-1):
        min_energy_above = min_energy_pixel(
            cem, *removed_pixels[-1], return_type="index"
            )
        removed_pixels.append(min_energy_above)

    removed_pixels_list_form = [c_w*pixel[0]+pixel[1] for pixel in removed_pixels]
    return removed_pixels_list_form[::-1]

def image_without_seam(image, seam):
    """
    Given a (color) image and a list of indices to be removed from the image,
    return a new image (without modifying the original) that contains all the
    pixels from the original image except those corresponding to the locations
    in the given list.
    """
    pixels = image["pixels"]
    out = {
        "width":image["width"],
        "height":image["height"],
        "pixels":pixels[:]
    }
    for rem_pixel in seam:
        out["pixels"][rem_pixel] = None
    while None in out["pixels"]:
        out["pixels"].remove(None)
    out["width"] -= 1
    return out

# VIGNETTE FUNCTION


def custom_feature(image, factor=1):
    """
    Returns a new image with the vignette filter, 
    where *factor* is the amount of vignette applied.

    Uses uses cosine of the distance from the center to compute the scaling factor.

    1 is a standard vignette.
    """
    def distance(r1,r2):
        return math.sqrt((r1[0]-r2[0])**2+(r1[1]-r2[1])**2)

    im_h = image["height"]
    im_w = image["width"]
    pixels = image["pixels"]

    out = {
        "width": im_w,
        "height": im_h,
        "pixels": pixels[:]
    }

    midpoint = (im_h//2,im_w//2)

    for ir in range(im_h):
        for ic in range(im_w):
            dis = distance(midpoint,(ir,ic))
            scale = (math.cos(dis*math.pi/math.sqrt(im_w**2+im_h**2)))**(2*factor)
            new_color = []
            for color in get_pixel(image,ir,ic):
                new_color.append(round(color*scale))
            set_pixel(out,ir,ic,tuple(new_color))

    return out


# HELPER FUNCTIONS FOR LOADING AND SAVING COLOR IMAGES


def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_color_image("test_images/cat.png")
    """
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img = img.convert("RGB")  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        width, height = img.size
        return {"height": height, "width": width, "pixels": pixels}


def save_color_image(image, filename, mode="PNG"):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the "mode" parameter.
    """
    out = Image.new(mode="RGB", size=(image["width"], image["height"]))
    out.putdata(image["pixels"])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns an instance of this class
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image("test_images/cat.png")
    """
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith("RGB"):
            pixels = [
                round(0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]) for p in img_data
            ]
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
    # cat_color = load_color_image("test_images/cat.png")
    # color_inverted = color_filter_from_greyscale_filter(inverted)
    # save_color_image(color_inverted(cat_color),"cat_color_inv.png")

    # python_color = load_color_image("test_images/python.png")
    # blur_9 = make_blur_filter(9)
    # blur_color = color_filter_from_greyscale_filter(blur_9)
    # save_color_image(blur_color(python_color), "python_blur9.png")

    # sparrow_color = load_color_image("test_images/sparrowchick.png")
    # sharpen_7 = make_sharpen_filter(7)
    # sharpen_color = color_filter_from_greyscale_filter(sharpen_7)
    # save_color_image(sharpen_color(sparrow_color),"sparrow_sharpen7.png")

    # filter1 = color_filter_from_greyscale_filter(edges)
    # filter2 = color_filter_from_greyscale_filter(make_blur_filter(5))
    # filt = filter_cascade([filter1, filter1, filter2, filter1])

    # frog_color = load_color_image("test_images/frog.png")
    #save_greyscale_image(greyscale_image_from_color_image(frog_color),"grey_frog.png")
    # save_color_image(filt(frog_color), "filt_frog.png")

    twocats = load_color_image("test_images/twocats.png")
    save_color_image(seam_carving(twocats, 100),"seam_removed_twocats.png")
    # save_color_image(custom_feature(twocats,1),"vignette_twocats.png")
