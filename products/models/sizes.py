from django.db import models


class SizeTable(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    filter_name = models.CharField(max_length=255, blank=True, null=True)
    category = models.ManyToManyField("products.Category", related_name='size_tables', blank=True)
    gender = models.ManyToManyField("products.Gender", related_name='size_tables', blank=True)
    size_rows = models.ManyToManyField("SizeRow", related_name='size_tables', blank=True)
    default_row = models.ForeignKey("SizeRow", related_name='default_size_table', blank=True, on_delete=models.PROTECT,
                                    null=True)
    standard = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}"


class SizeRow(models.Model):
    filter_name = models.CharField(max_length=128, default="")
    filter_logo = models.CharField(max_length=128, default="")
    sizes = models.JSONField(default=list)


class SizeTranslationRows(models.Model):
    table = models.ForeignKey("SizeTable", blank=True, null=True, on_delete=models.CASCADE, related_name="rows",
                              db_index=True)
    row = models.JSONField(blank=True, null=True)
    is_one_size = models.BooleanField(default=False, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['id']), models.Index(fields=['is_one_size'])]

    def __str__(self):
        return f"{self.table} {self.id}"
