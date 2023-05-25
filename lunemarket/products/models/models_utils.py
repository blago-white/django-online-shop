import hashlib
import random

from django.db import models

from .. import filters


def get_image_path(self: models.Model, filename: str) -> str:
    return _form_load_path_to_image(target_dir=_get_target_directory(model=self),
                                    img_hash=_get_image_name(filename=filename),
                                    img_extension=_get_file_extension(filename=filename),
                                    object_title=self.title)


def _form_load_path_to_image(**path_parts: dict) -> str:
    try:
        target_dir = path_parts['target_dir']
        object_title = filters.spaces_to_dashes(path_parts['object_title'])
        image_name = ".".join((path_parts['img_hash'], path_parts['img_extension']))

        return '/'.join((target_dir, object_title, image_name))

    except KeyError:
        raise KeyError(f"Not all arguments for making a path have been received, received: {path_parts.keys()}")


def _get_image_name(filename: str) -> str:
    filename = "".join(random.choice(list(filename)))
    return hashlib.sha256(filename.encode("utf-8")).hexdigest()


def _get_target_directory(model: models.Model) -> str:
    return model.__class__.__name__.lower()


def _get_file_extension(filename: str) -> str:
    return filename.split(".")[-1]
