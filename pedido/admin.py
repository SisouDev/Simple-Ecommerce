from django.contrib import admin
from .models import Pedido, ItemDoPedido

class ItemPedidoInLine(admin.TabularInline):
    model = ItemDoPedido
    extra = 1

class PedidoAdmin(admin.ModelAdmin):
    inlines = [
        ItemPedidoInLine
    ]

admin.site.register(Pedido, PedidoAdmin)
admin.site.register(ItemDoPedido)
