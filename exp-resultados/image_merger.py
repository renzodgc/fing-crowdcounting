import glob
import os
from PIL import Image

DATASETS = ["MT", "SHA", "SHB", "UCF-CC50", "UCF-QNRF"]
LWCC = "LWCC"
SASNET = "SASNet"
TOP_MARGIN = 31
MARGIN = 10

ROOT = "d:/OneDrive - Facultad de Ingeniería/Documents/Academics/fing-crowdcounting/exp-resultados"
# ROOT = "/home/renzo/fing/fing-crowdcounting/exp-resultados"

def get_vertical_boundary(img: Image, start: int, middle: int, end: int):
    img = img.convert("L")
    u, l = start, end
    for y in reversed(range(start, middle)):
        if all([img.getpixel((x,y)) == 255 for x in range(MARGIN, img.width - MARGIN)]):
            u = y - TOP_MARGIN
            break
    for y in range(middle, end):
        if all([img.getpixel((x,y)) == 255 for x in range(MARGIN, img.width - MARGIN)]):
            l = y-1
            break
    return u, l

def get_vertical_boundaries(col: Image):
    col = col.convert("L")
    row_1_u, row_1_l = get_vertical_boundary(col, 0, col.height//6, col.height//3) # First image
    row_2_u, row_2_l = get_vertical_boundary(col, col.height//3, col.height//2, 2*col.height//3) # Second image
    row_3_u, row_3_l = get_vertical_boundary(col, 2*col.height//3, 5*col.height//6, col.height) # Third image
    return row_1_u, row_1_l, row_2_u, row_2_l, row_3_u, row_3_l,

def get_lr_borders(img: Image):
    img = img.convert("L")
    hx = img.width//2
    hy = img.height//2
    for x in range(0, hx):
        if img.getpixel((x,hy)) != 255:
            left = x
            break
    for x in range(hx, img.width):
        if img.getpixel((x,hy)) == 255:
            right = x
            break
    return left, right

def get_rows(col: Image):
    left, right = get_lr_borders(col)
    col = col.crop((left, 0, right, col.height))

    row_1_u, row_1_l, row_2_u, row_2_l, row_3_u, row_3_l = get_vertical_boundaries(col)
    # crop((left, upper, right, lower))
    img_1 = col.crop((0, row_1_u, col.width, row_1_l))
    img_2 = col.crop((0, row_2_u, col.width, row_2_l))
    img_3 = col.crop((0, row_3_u, col.width, row_3_l))
    return img_1, img_2, img_3

def get_individual_images(lwcc: Image, sasnet: Image) -> Image:
    # crop((left, upper, right, lower))
    sasnet_sha = sasnet.crop((sasnet.width//2, 0, 3*sasnet.width//4, sasnet.height))
    sasnet_sha_left, sasnet_sha_right = get_lr_borders(sasnet_sha)
    sasnet_sha = sasnet_sha.crop((sasnet_sha_left, 0, sasnet_sha_right, sasnet_sha.height))

    sasnet_shb = sasnet.crop((int(3.02*sasnet.width/4), 0, sasnet.width, sasnet.height))
    sasnet_shb_left, sasnet_shb_right = get_lr_borders(sasnet_shb)
    sasnet_shb = sasnet_shb.crop((sasnet_shb_left, 0, sasnet_shb_right, sasnet_shb.height))

    col_1 = lwcc.crop((0, 0, lwcc.width//4, lwcc.height))
    col_2 = lwcc.crop((lwcc.width//4, 0, lwcc.width//2, lwcc.height))
    col_3 = lwcc.crop((lwcc.width//2, 0, 3*lwcc.width//4, lwcc.height))
    col_4 = lwcc.crop((3*lwcc.width//4, 0, lwcc.width, lwcc.height))

    original_image, bay_sha, dmcount_shb = get_rows(col_1)
    gt, bay_shb, dmcount_qnrf = get_rows(col_2)
    csrnet_sha, bay_qnrf, sfa_shb = get_rows(col_3)
    csrnet_shb, dmcount_sha, _ = get_rows(col_4)

    return original_image, gt, csrnet_sha, csrnet_shb, bay_sha, bay_shb, bay_qnrf, dmcount_sha, dmcount_shb, dmcount_qnrf, sfa_shb, sasnet_sha, sasnet_shb

def merge_images_vertical(lwcc: Image, sasnet: Image) -> Image:
    original_image, gt, csrnet_sha, csrnet_shb, bay_sha, bay_shb, bay_qnrf, dmcount_sha, dmcount_shb, dmcount_qnrf, sfa_shb, sasnet_sha, sasnet_shb = get_individual_images(lwcc, sasnet)

    merged_image = Image.new('RGB', (3*(original_image.width + MARGIN) + MARGIN, 6*(original_image.height + MARGIN)), color="white")
    row_height = 0
    # Row 1
    merged_image.paste(original_image, (merged_image.width//3 + MARGIN - original_image.width//2, row_height))
    merged_image.paste(gt, (2*merged_image.width//3 + MARGIN - gt.width//2, row_height))
    row_height += original_image.height + MARGIN

    # Row 2
    merged_image.paste(csrnet_shb, (MARGIN, row_height))
    merged_image.paste(csrnet_sha, (csrnet_shb.width + 2*MARGIN, row_height))
    row_height += csrnet_shb.height + MARGIN

    # Row 3
    merged_image.paste(sasnet_shb, (MARGIN, row_height))
    merged_image.paste(sasnet_sha, (sasnet_shb.width + 2*MARGIN, row_height))
    row_height += sasnet_shb.height + MARGIN

    # Row 4
    row_width = MARGIN
    merged_image.paste(bay_shb, (row_width, row_height))
    row_width += bay_shb.width + MARGIN
    merged_image.paste(bay_sha, (row_width, row_height))
    row_width += bay_sha.width + MARGIN
    merged_image.paste(bay_qnrf, (row_width, row_height))
    row_height += bay_shb.height + MARGIN

    # Row 5
    row_width = MARGIN
    merged_image.paste(dmcount_shb, (row_width, row_height))
    row_width += dmcount_shb.width + MARGIN
    merged_image.paste(dmcount_sha, (row_width, row_height))
    row_width += dmcount_sha.width + MARGIN
    merged_image.paste(dmcount_qnrf, (row_width, row_height))
    row_height += dmcount_shb.height + MARGIN

    # Row 6
    merged_image.paste(sfa_shb, (merged_image.width - sfa_shb.width - 2*MARGIN, row_height))

    return merged_image

def merge_images_horizontal(lwcc: Image, sasnet: Image) -> Image:
    original_image, gt, csrnet_sha, csrnet_shb, bay_sha, bay_shb, bay_qnrf, dmcount_sha, dmcount_shb, dmcount_qnrf, sfa_shb, sasnet_sha, sasnet_shb = get_individual_images(lwcc, sasnet)

    merged_image = Image.new('RGB', (6*(original_image.width + MARGIN) + MARGIN, 3*(original_image.height + MARGIN) + MARGIN), color="white")
    row_width = MARGIN
    # Row 1
    merged_image.paste(original_image, (row_width, merged_image.height//3 + MARGIN - gt.height//2))
    merged_image.paste(gt, (row_width, 2*merged_image.height//3 + MARGIN - gt.height//2))
    row_width += original_image.width + MARGIN

    # Row 2
    merged_image.paste(csrnet_shb, (row_width, MARGIN))
    merged_image.paste(csrnet_sha, (row_width, csrnet_shb.height + 2*MARGIN))
    row_width += csrnet_shb.width + MARGIN

    # Row 3
    merged_image.paste(sasnet_shb, (row_width, 3))
    merged_image.paste(sasnet_sha, (row_width, sasnet_shb.height))
    row_width += sasnet_shb.width + MARGIN

    # Row 4
    merged_image.paste(bay_shb, (row_width, MARGIN))
    merged_image.paste(bay_sha, (row_width, bay_shb.height + 2*MARGIN))
    merged_image.paste(bay_qnrf, (row_width, 2*bay_shb.height + 3*MARGIN))
    row_width += bay_shb.width + MARGIN

    # Row 5
    merged_image.paste(dmcount_shb, (row_width, MARGIN))
    merged_image.paste(dmcount_sha, (row_width, dmcount_shb.height + 2*MARGIN))
    merged_image.paste(dmcount_qnrf, (row_width, 2*dmcount_shb.height + 3*MARGIN))
    row_width += dmcount_shb.width + MARGIN

    # Row 6
    merged_image.paste(sfa_shb, (row_width, merged_image.height - sfa_shb.height - MARGIN))

    return merged_image

for dataset in DATASETS:
    lwcc_paths = glob.glob(f"{ROOT}/{dataset}/{LWCC}/*.png")
    img_basenames = [os.path.basename(p) for p in lwcc_paths]
    print("Processing images for", dataset)
    lwcc_images = [Image.open(p) for p in lwcc_paths]
    sasnet_images = [Image.open(p.replace(LWCC, SASNET)) for p in lwcc_paths]
    for lwcc, sasnet, base_name in zip(lwcc_images, sasnet_images, img_basenames):
        merged_image = merge_images_horizontal(lwcc, sasnet)
        merged_image.save(f"{ROOT}/{dataset}/{base_name}")
