import shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import os
import time
import normalize

def list_files_in_directory(path):
    file_list = []

    for path in Path(path).rglob('*'):
        if path.is_file():
            new_path = path.parent / normalize(path.name)
            path.rename(new_path)
            file_list.append((new_path.name, new_path))

    return file_list

def rename_files(file_list):
    file_name_counts = {}
    new_file_list = []

    for file_name, file_path in file_list:
        base_name, ext = os.path.splitext(file_name)
        if file_name in file_name_counts:
            file_name_counts[file_name] += 1
            new_file_name = f"{base_name}({file_name_counts[file_name]}){ext}"
        else:
            file_name_counts[file_name] = 0
            new_file_name = file_name
        
        new_file_path = os.path.join(os.path.dirname(file_path), new_file_name)
        new_file_list.append((new_file_name, new_file_path))
    
    return new_file_list

def compare_and_rename(file_list, new_file_list):
    for (name, path), (new_name, new_path) in zip(file_list, new_file_list):
        if name != new_name:
            path.rename(path.with_name(new_name))

folder_names = ('images','video','documents','audio','archives','unknown')  


def add_new_folders(path, folder_names):
    folder_paths = {}
    for folder_name in folder_names:
        folder_path = os.path.join(path, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        folder_paths[folder_name] = folder_path
    return folder_paths

def del_folders(path):
    all_dirs = os.listdir(path)
    for item in all_dirs:
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path) and item not in folder_names:
            shutil.rmtree(item_path)

def archives_unpack(path):
    ARCHIVES_PATH = Path(path) / 'archives'
    for archive_file in ARCHIVES_PATH.iterdir():
        if archive_file.is_file() and archive_file.suffix in ('.zip', '.tar', '.tar.gz', '.tar.bz2', '.tar.xz'):
            new_archive_path = ARCHIVES_PATH / archive_file.stem
            new_archive_path.mkdir(parents=True, exist_ok=True)
            shutil.unpack_archive(archive_file, new_archive_path)

def sort_folders(path):
    
    images = ('JPEG', 'PNG', 'JPG', 'SVG')
    video =('AVI', 'MP4', 'MOV', 'MKV')
    doc=('DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX')
    audio=('MP3', 'OGG', 'WAV', 'AMR')
    arch=('ZIP', 'GZ', 'TAR','RAR')
    known_ext = []
    unknown_ext = []

    old_file_list = list_files_in_directory(path)
    new_file_list = rename_files(old_file_list)
    compare_and_rename(old_file_list, new_file_list)
    folder_path = add_new_folders(path, folder_names)

    def move_file(file_name, file_path):
        nonlocal known_ext
        nonlocal unknown_ext
        filename, fileext = os.path.splitext(file_name)
        file_ext = fileext[1:].upper()
        if file_ext in images:
            known_ext.append(file_ext)
            shutil.move(file_path, folder_path['images'])
        elif file_ext in video:
            known_ext.append(file_ext)
            shutil.move(file_path, folder_path['video'])
        elif file_ext in doc:
            known_ext.append(file_ext)
            shutil.move(file_path, folder_path['documents'])
        elif file_ext in audio:
            known_ext.append(file_ext)
            shutil.move(file_path, folder_path['audio'])
        elif file_ext in arch:
            known_ext.append(file_ext)
            shutil.move(file_path, folder_path['archives'])
        else:
            unknown_ext.append(file_ext)
            shutil.move(file_path, folder_path['unknown'])

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(lambda x: move_file(*x), new_file_list)

    del_folders(path)
    archives_unpack(path)

    print(f'Відомі розширення: {known_ext}')
    print(f'Невідомі розширення: {unknown_ext}')

if __name__ == "__main__":
    folder_process = Path(r"C:\Users\user\Desktop\test")
    start_time = time.time()
    sort_folders(folder_process.resolve())
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Час виконання: {elapsed_time} секунд")
