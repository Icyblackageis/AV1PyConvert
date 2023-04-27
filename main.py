from av1pyconvert import av1pyconvert

orig_folder_path = input("Enter the path to the original videos folder: ")
enc_folder_path = input("Enter the path to the output videos folder: ")
crf_value = input("Enter the CRF value (recommended range is 35-25): ")

av1pyconvert(orig_folder_path, enc_folder_path, crf_value)
