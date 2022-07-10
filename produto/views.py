from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views import View
from .models import Produto, Variacao
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from perfil.models import Perfil



class ListaProdutos(ListView):
    model = Produto
    template_name = 'produto/lista.html'
    context_object_name = 'produtos'
    paginate_by = 6
    ordering = ['-id']


class DetalheProdutos(DetailView):
    model = Produto
    template_name = 'produto/detalhe.html'
    context_object_name = 'produto'
    slug_url_kwarg = 'slug'


class AddCarrinho(View):
    def get(self, *args, **kwargs):
        # TODO remover if self.request.session.get('carrinho'):
            #del self.request.session['carrinho']
            #self.request.session.save()

        http_referer = self.request.META.get(
            'HTTP_REFERER',
            reverse('produto:lista')
        )
        variacao_id = self.request.GET.get('vid')

        if not variacao_id:
            messages.error(
                self.request,
                'Produto não existe'
            )
            return redirect(http_referer)

        variacao = get_object_or_404(Variacao, id=variacao_id)

        variacao_estoque = variacao.estoque

        produto = variacao.produto

        produto_id = produto.id
        produto_nome = produto.nome
        variacao_nome = variacao.nome or ''
        preco_unitario = variacao.preco_var
        preco_unitario_promocional = variacao.preco_promocional
        quantidade = 1
        slug = produto.slug
        imagem = produto.imagem 

        if imagem:
            imagem = imagem.name
        else:
            imagem = ''


        if variacao.estoque < 1:
            messages.error(
                self.request,
                'Estoque insuficiente.',
            )
            return redirect(http_referer)

        if not self.request.session.get('carrinho'):
            self.request.session['carrinho'] = {}
            self.request.session.save()

        carrinho = self.request.session['carrinho']

        if variacao_id in carrinho:
            quantidade_carrinho = carrinho[variacao_id]['quantidade']
            quantidade_carrinho += 1
            
            if variacao_estoque < quantidade_carrinho:
                messages.warning(
                    self.request,
                    f'Estoque insuficiente para {quantidade_carrinho}x no produto "{produto_nome}".\nAdicionamos {variacao_estoque}x no seu carrinho.'
                )
                quantidade_carrinho = variacao_estoque
            
            carrinho[variacao_id]['quantidade'] = quantidade_carrinho
            carrinho[variacao_id]['preco_quantitativo'] = preco_unitario * quantidade_carrinho
            carrinho[variacao_id]['preco_quantitativo_promocional'] = preco_unitario_promocional * quantidade_carrinho

        else:
            carrinho[variacao_id] = {
                'produto_id': produto_id,
                'produto_nome': produto_nome,
                'variacao_nome': variacao_nome,
                'variacao_id': variacao_id,
                'preco_unitario': preco_unitario,
                'preco_unitario_promocional': preco_unitario_promocional,
                'preco_quantitativo': preco_unitario,
                'preco_quantitativo_promocional': preco_unitario_promocional,
                'quantidade': quantidade,
                'slug': slug,
                'imagem': imagem,
            }

        self.request.session.save()
        messages.success(
            self.request,
            f'Produto {produto_nome} {variacao_nome} adicionado ao seu carrinho {carrinho[variacao_id]["quantidade"]}x '
        )
        return redirect(http_referer)



class RemoverCarrinho(View):
    def get(self, *args, **kwargs):
        http_referer = self.request.META.get(
            'HTTP_REFERER',
            reverse('produto:lista')
        )
        variacao_id = self.request.GET.get('vid')

        if not variacao_id:
            return redirect(http_referer)

        if not self.request.session.get('carrinho'):
            return redirect(http_referer)

        if variacao_id not in self.request.session.get('carrinho'):
            return redirect(http_referer)
        
        carrinho = self.request.session['carrinho'][variacao_id]

        messages.success(
            self.request,
            f'Produto {carrinho["produto_nome"]} {carrinho["variacao_nome"]} removido do seu carrinho.'
        )

        del self.request.session['carrinho'][variacao_id]
        self.request.session.save()
        return redirect(http_referer)



class Carrinho(View):
    def get(self, *args, **kwargs):
        contexto = {
            'carrinho' : self.request.session.get('carrinho',{})
        }
        return render(self.request, 'produto/carrinho.html', context=contexto)


class Finalizar(View):
    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('perfil:criar')

        perfil = Perfil.objects.filter(usuario=self.request.user).exists()

        if not perfil:
            messages.error(
                self.request, 'Usuário não possui perfil.'
            )
            return redirect('perfil:criar')
        
        if not self.request.session.get('carrinho'):
            messages.warning(
                self.request, 'Seu carrinho está vazio.'
            )
            return redirect('produto:lista')

        
        contexto = {
            'usuario': self.request.user,
            'carrinho': self.request.session['carrinho'],
        }
        return render(self.request, 'produto/finalizar.html', contexto)
