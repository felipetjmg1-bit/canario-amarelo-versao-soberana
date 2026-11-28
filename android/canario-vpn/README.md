# Canário VPN (Android)

Aplicativo Android nativo Java da Impulso Digital Soluções em IA.

## Estado desta versão
- Interface escura e painel de tempo.
- Recompensa de +15 minutos em modo simulado local.
- Cronômetro de sessão e métricas TrafficStats do dispositivo.
- Estrutura Android VpnService e notificação persistente.
- A tela informa explicitamente que o gateway ainda não está configurado.

**Não é ainda uma VPN de produção.** O serviço não cria uma rota TUN nem encaminha pacotes. Antes de oferecer conectividade real, provisionar um gateway e integrar um protocolo auditado (por exemplo, WireGuard via biblioteca oficial), com gestão segura de chaves, DNS, IPv4/IPv6, kill switch e testes de vazamento.

O espaço de banner e o botão de recompensa são placeholders. Para anúncios reais, integrar Google Mobile Ads Rewarded Ads com IDs de teste durante desenvolvimento, validação de recompensa no callback e política de consentimento aplicável.

## Build
Abra esta pasta como projeto Gradle no Android Studio ou execute:
`gradle assembleDebug`
O APK de debug sai em `app/build/outputs/apk/debug/app-debug.apk`.

## Instalação
Baixe o APK debug do workflow, permita instalação pelo navegador/gerenciador de arquivos quando solicitado e instale. É uma build de teste, não uma versão assinada para distribuição pública.
