from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from PIL import Image
import os
# Create your models here.

class Poll(models.Model):
    title = models.CharField(max_length=100)
    question = models.CharField(max_length=250)
    question_image = models.ImageField(blank=True, upload_to='question_image')
    time_posted = models.DateTimeField(default=timezone.now)
    voters = models.ManyToManyField(User, related_name='voters')
    #considering global polls can never be deleted by any user
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    link = models.CharField(max_length=10)

    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse("poll-detail", kwargs={"link": self.link})
    def save(self,*args, **kwargs):
        super().save(*args, **kwargs)
        try:
            img = Image.open(self.question_image.path)
            output_size = (300,300)
            if img.height > 300 or img.width > 300:
                img.thumbnail(output_size)
                img.save(self.question_image.path)
        except:
            print('Image is not required')

    def delete(self, *args, **kwargs):
        try:
            url = self.question_image.url
            print('here')
            os.remove(url)
            print('here2')
        except:
            print('No image present')

        users = self.voters.all()
        for user in users:
            self.voters.remove(user)
        super().delete( self, *args, **kwargs)
        
        
    
class Choice(models.Model):
    choice_text = models.CharField(max_length=100)
    choice_image= models.ImageField(blank = True,upload_to='choice_image')
    choice_count = models.PositiveSmallIntegerField(default=0)
    poll = models.ForeignKey(Poll, on_delete= models.CASCADE)

    def __str__(self):
        return self.choice_text

    def save(self,*args, **kwargs):
        super().save(*args, **kwargs)
        try:
            img = Image.open(self.choice_image.path)
            output_size = (150,150)
            if img.height > 150 or img.width > 150:
                img.thumbnail(output_size)
                img.save(self.choice_image.path)
        except:
            print('Image is not required')

    def delete(self, *args, **kwargs):
        try:
            url = self.choice_image.url
            os.remove(url)
        except:
            print('No image present')
        super().delete(self,*args, **kwargs)
        