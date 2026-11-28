# Canário VPN — gateway WireGuard

## Estado

O aplicativo Android ainda não possui um gateway. Esta pasta documenta a infraestrutura necessária; ela **não cria um servidor automaticamente** e não contém chaves privadas.

## Requisitos mínimos do servidor

- VPS Linux Ubuntu 24.04 LTS (ou distribuição suportada pelo WireGuard)
- IPv4 público dedicado ou endereço público estável
- UDP/51820 liberado no firewall do provedor e no firewall do sistema
- Acesso administrativo para instalar e configurar WireGuard
- Orçamento/assinatura do provedor de VPS: não há servidor gratuito garantido

Para um primeiro teste pessoal, uma VPS pequena (1 vCPU e 1 GB RAM) costuma ser suficiente; dimensionamento final depende do número de usuários e tráfego. Escolha região próxima dos usuários, preferencialmente Brasil, para reduzir latência.

## Arquitetura

Android (Canário VPN + biblioteca oficial WireGuard) -> túnel WireGuard UDP -> VPS -> NAT/encaminhamento -> Internet.

O servidor precisa gerar um par de chaves e um perfil de cliente exclusivo. O perfil contém endpoint público, chave pública do servidor, chave privada do cliente, endereço interno e DNS. **Nunca publique ou envie a chave privada do servidor ao aplicativo.** A chave privada do cliente deve ser tratada como segredo e não deve ser commitada no Git.

## Provisionamento manual (Ubuntu)

1. Crie a VPS e confirme que o provedor permite tráfego UDP na porta 51820.
2. Atualize o sistema e instale WireGuard:
   `sudo apt update && sudo apt install -y wireguard`
3. Habilite encaminhamento IPv4 (e IPv6 somente se for configurado de ponta a ponta):
   `echo 'net.ipv4.ip_forward=1' | sudo tee /etc/sysctl.d/99-canario-vpn.conf`
   `sudo sysctl --system`
4. Gere as chaves no próprio servidor, com permissões restritas:
   `umask 077 && wg genkey | tee server_private.key | wg pubkey > server_public.key`
5. Configure a interface `wg0`, o peer cliente, NAT e regras de firewall de acordo com a interface de rede pública real da VPS. Não copie regras de NAT sem identificar a interface de saída e o firewall ativo.
6. Inicie e habilite `wg-quick@wg0`; valide `sudo wg show`, handshake, DNS, IPv4/IPv6 e vazamento de tráfego.
7. Gere um perfil de cliente separado. Mantenha a chave privada do cliente fora do repositório e compartilhe-a somente por canal seguro com o proprietário do dispositivo.

## Integração Android pendente

A próxima etapa do app é integrar a biblioteca oficial `com.wireguard.android:tunnel`, permitir importar um perfil `.conf` e controlar o estado real do túnel. A tela não deve declarar "conectado" até que o backend WireGuard confirme a interface ativa e o handshake com o gateway.

Referências:
- https://www.wireguard.com/quickstart/
- https://www.wireguard.com/embedding/
- https://developer.android.com/develop/connectivity/vpn

## Segurança e privacidade

- Não use VPN para contornar cobrança, limites de franquia ou controles da operadora.
- Não reutilize a mesma chave de cliente em vários dispositivos.
- Não registre tráfego, credenciais ou conteúdo de navegação dos usuários.
- Publique política de privacidade e informe claramente o operador do servidor, retenção de logs e limites do serviço.
- Faça testes de DNS, IPv4, IPv6, reconexão, troca Wi-Fi/dados móveis e kill switch antes de produção.
