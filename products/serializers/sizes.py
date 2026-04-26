from rest_framework import serializers

from products.models import SizeRow, SizeTable, SizeTranslationRows


class SizeRowSerializer(serializers.ModelSerializer):
    is_main = serializers.SerializerMethodField()

    class Meta:
        model = SizeRow
        fields = '__all__'

    def get_is_main(self, row):
        user = self.context.get('user')
        if user is not None and row.size_tables.first().name not in ["Shoes_Adults", "Clothes_Men" "Clothes_Women"]:
            return user.preferred_shoes_size_row == row or user.preferred_clothes_size_row == row

        return row == row.size_tables.first().default_row


class SizeTableSerializer(serializers.ModelSerializer):
    size_rows = serializers.SerializerMethodField()

    class Meta:
        model = SizeTable
        exclude = ['default_row', 'category', 'gender', 'standard']
        depth = 2

    def get_size_rows(self, obj):
        size_rows = obj.size_rows.order_by('id')
        serializer = SizeRowSerializer(size_rows, many=True)
        return serializer.data


class SizeTranslationRowsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SizeTranslationRows
        fields = '__all__'
