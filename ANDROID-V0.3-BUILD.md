# CANÁRIO AMARELO Android V0.3

Esta branch foi preparada para compilar o pacote Android V0.3 sem alterar a branch principal.

## Como gerar o APK

1. Envie o arquivo `CANARIO_AMARELO_Android_V0.3.zip` para a raiz desta branch (`android-v0.3-build`).
2. Acesse a aba **Actions**.
3. Abra **CANARIO AMARELO Android V0.3 - Build APK**.
4. A execução inicia após o upload. Se necessário, use **Run workflow**.
5. Aguarde o resultado. Em caso de sucesso, abra a execução e baixe o artefato `canario-amarelo-v0.3-debug-apk`.
6. Extraia o ZIP do artefato e instale `app-debug.apk` no Android.

O ZIP do projeto é código-fonte, não é o APK. O APK só é produzido se a compilação e os testes passarem. Esta é uma versão debug para avaliação, não assinada para publicação na Play Store.
