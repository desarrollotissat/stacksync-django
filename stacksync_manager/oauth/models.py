from django.db import models
from users.models import StacksyncUser


class Consumer(models.Model):

    id = models.AutoField(primary_key=True)
    consumer_key = models.CharField(max_length=100)
    consumer_secret = models.CharField(max_length=100)
    rsa_key = models.CharField(max_length=100)
    user = models.ForeignKey(StacksyncUser, db_column="user")
    realm = models.CharField(max_length=100)
    redirect_uri = models.CharField(max_length=100)
    application_title = models.CharField(max_length=100)
    application_description = models.CharField(max_length=100)
    application_uri = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "oauth1_consumers"

    def __unicode__(self):
        return self.user


class RequestToken(models.Model):

    id = models.AutoField(primary_key=True)
    consumer = models.ForeignKey(Consumer, db_column="consumer")
    user = models.ForeignKey(StacksyncUser, db_column="user")
    realm = models.CharField(max_length=100)
    redirect_uri = models.CharField(max_length=100)
    request_token = models.CharField(max_length=100)
    request_token_secret = models.CharField(max_length=100)
    verifier = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "oauth1_request_tokens"

    def __unicode__(self):
        return u'%s - %s - %s' % (self.request_token, self.request_token_secret, self.verifier)


class AccessToken(models.Model):

    id = models.AutoField(primary_key=True)
    consumer = models.ForeignKey(Consumer, db_column="consumer")
    user = models.ForeignKey(StacksyncUser, db_column="user")
    realm = models.CharField(max_length=100)
    access_token = models.CharField(max_length=100)
    access_token_secret = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "oauth1_access_tokens"

    def __unicode__(self):
        return u'%s - %s' % (self.access_token, self.access_token_secret)


class Nonce(models.Model):

    id = models.AutoField(primary_key=True)
    consumer_key = models.CharField(max_length=100, db_column='consumer_key')
    token = models.CharField(max_length=100)
    timestamp = models.IntegerField()
    nonce = models.CharField(max_length=100)

    class Meta:
        db_table = "oauth1_nonce"
        unique_together = (('consumer_key', 'token', 'timestamp', 'nonce'),)
