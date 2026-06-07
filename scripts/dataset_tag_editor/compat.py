from modules import shared

OPTS_DEFAULTS = {
    'dataset_editor_batch_size_vit': 4,
    'dataset_editor_batch_size_convnext': 4,
    'dataset_editor_batch_size_swinv2': 4,
    'dataset_editor_max_res': 0,
    'dataset_editor_use_temp_files': False,
    'dataset_editor_use_raw_clip_token': True,
    'dataset_editor_use_rating': False,
    'dataset_editor_num_cpu_workers': -1,
    'dataset_filename_join_string': ' ',
    'dataset_filename_word_regex': '',
    'interrogate_keep_models_in_memory': False,
    'interrogate_clip_max_length': 77,
    'interrogate_deepbooru_score_threshold': 0.5,
    'deepbooru_use_spaces': True,
    'deepbooru_escape': True,
}

def patch_opts():
    for key, value in OPTS_DEFAULTS.items():
        if not hasattr(shared.opts, key):
            setattr(shared.opts, key, value)