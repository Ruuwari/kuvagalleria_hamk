from django.db import models
from PIL import Image
from io import BytesIO
import os.path
from django.core.files.base import ContentFile

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return self.name

class Photo(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(null=False, blank=False)
    description = models.TextField()
    thumbnail = models.ImageField(editable=False, null=True)

    def save(self, *args, **kwargs):

        if not self.make_thumbnail():
            raise Exception("Could not create thumbnail")
        
        super(Photo, self).save(*args, **kwargs)

    def make_thumbnail(self):

        im = Image.open(self.image)
        width, height = im.size
        ratio = width/height
        new_width = 640
        new_height = new_width/ratio
        thumb = im.resize((round(new_width), round(new_height)), Image.ANTIALIAS)

        thumb_name, thumb_extension = os.path.splitext(self.image.name)
        thumb_extension = thumb_extension.lower()

        thumb_filename = thumb_name + '_thumbnail' + thumb_extension

        if thumb_extension in ['.jpg', '.jpeg']:
            FTYPE = 'JPEG'
        elif thumb_extension == '.gif':
            FTYPE = 'GIF'
        elif thumb_extension == '.png':
            FTYPE = 'PNG'
        else:
            return False  # Unrecognized file type
        
        # Save thumbnail to in-memory file as stringIO
        temp_thumb = BytesIO()
        thumb.save(temp_thumb, FTYPE)
        temp_thumb.seek(0)

        self.thumbnail.save(thumb_filename, ContentFile(temp_thumb.read()), save=False)
        temp_thumb.close()

        return True


    def __str__(self):
        return self.description