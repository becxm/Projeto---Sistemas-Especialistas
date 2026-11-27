# Dicionário de regras e fatos

Gerado automaticamente por `python scripts/gerar_docs_regras.py` a partir de `data/regras.json` e `data/fatos.json`.
O CF (fator de certeza) de cada regra é uma **estimativa heurística da equipe**, não um valor calibrado estatisticamente.
Regras com origem **extensão** não constam do Plano de Projeto; foram criadas para o encadeamento em múltiplas etapas.

## Elétrica e Ignição

### E01 — Tensão abaixo de 13,5 V

- **Tipo:** intermediaria · **Origem:** extensao · **CF:** 1,0
- **SE:** Tensão medida na bateria (motor ligado) < 13,5
- **ENTÃO deduz:** `tensao_abaixo_13_5` = True
- **Explicação:** Extensão: converte a tensão numérica medida em um fato lógico utilizado pela Regra 04.

### E02 — Tensão em 13,5 V ou mais

- **Tipo:** intermediaria · **Origem:** extensao · **CF:** 1,0
- **SE:** Tensão medida na bateria (motor ligado) ≥ 13,5
- **ENTÃO deduz:** `tensao_abaixo_13_5` = False
- **Explicação:** Extensão: tensão normal de carga; descarta a hipótese de alternador sem carga.

### R01 — Bateria descarregada ou fim de vida útil

- **Tipo:** diagnostico · **Origem:** documento · **CF:** 0,9
- **SE:** Motor não gira ao virar a chave **E** Luzes do painel fracas **E** Clique ao virar a chave
- **ENTÃO diagnóstico =** Bateria descarregada ou fim de vida útil
- **Explicação:** Sem girar o motor, com luzes fracas e clique no solenoide, a bateria não fornece corrente suficiente para a partida.
- **Possíveis causas:** Bateria descarregada; Bateria no fim da vida útil
- **Recomendações (complementares):** Testar a carga da bateria; Fazer carga ou substituir a bateria; Verificar bornes e terminais
- **Especialista indicado:** Eletricista automotivo

### R02 — Falha na bomba de combustível ou sensor de rotação

- **Tipo:** diagnostico · **Origem:** documento · **CF:** 0,8
- **SE:** Motor gira bem, mas não pega **E** Luz de injeção acesa
- **ENTÃO diagnóstico =** Falha na bomba de combustível ou sensor de rotação
- **Explicação:** Motor girando sem pegar com a luz de injeção acesa indica falta de combustível ou perda do sinal de rotação para a central.
- **Possíveis causas:** Falha na bomba de combustível; Falha no sensor de rotação
- **Recomendações (complementares):** Medir pressão de combustível; Ler códigos de falha com scanner; Testar o sensor de rotação
- **Especialista indicado:** Eletricista automotivo

### R03 — Curto-circuito no chicote elétrico ou fusível principal rompido

- **Tipo:** diagnostico · **Origem:** documento · **CF:** 0,85
- **SE:** Cheiro de queimado **E** Fumaça no painel **E** Rádio ou luzes apagaram
- **ENTÃO diagnóstico =** Curto-circuito no chicote elétrico ou fusível principal rompido
- **Explicação:** Cheiro de queimado, fumaça no painel e perda de rádio/luzes apontam sobrecarga elétrica com fusível rompido ou fiação em curto.
- **Possíveis causas:** Curto-circuito no chicote elétrico; Fusível principal rompido
- **Recomendações (complementares):** Desligar a bateria imediatamente por segurança; Inspecionar chicote e caixa de fusíveis; Não substituir fusível por outro de maior amperagem
- **Especialista indicado:** Eletricista automotivo

### R04 — Falha no alternador (não está carregando a bateria)

- **Tipo:** diagnostico · **Origem:** documento · **CF:** 0,9
- **SE:** Bateria nova descarrega rápido **E** Tensão da bateria abaixo de 13,5 V (fato derivado)
- **ENTÃO diagnóstico =** Falha no alternador (não está carregando a bateria)
- **Explicação:** Bateria nova que descarrega rápido, com tensão abaixo de 13,5 V com o motor ligado, indica que o alternador não recarrega o sistema.
- **Possíveis causas:** Alternador com defeito; Regulador de tensão com defeito; Correia do alternador
- **Recomendações (complementares):** Testar a saída do alternador; Verificar correia e regulador de tensão; Substituir ou recondicionar o alternador
- **Especialista indicado:** Eletricista automotivo

## Motor e Câmbio

### R05 — Velas de ignição gastas ou cabos de vela com fuga de corrente

- **Tipo:** diagnostico · **Origem:** documento · **CF:** 0,85
- **SE:** Carro engasgando na aceleração **E** Perda de potência
- **ENTÃO diagnóstico =** Velas de ignição gastas ou cabos de vela com fuga de corrente
- **Explicação:** Engasgos na aceleração com perda de potência são típicos de falha de centelha nos cilindros.
- **Possíveis causas:** Velas de ignição gastas; Cabos de vela com fuga de corrente
- **Recomendações (complementares):** Inspecionar e trocar o jogo de velas; Testar a isolação dos cabos de vela
- **Especialista indicado:** Mecânico de motor e câmbio

### R06 — Motor queimando óleo (anéis de segmento ou retentores de válvula)

- **Tipo:** diagnostico · **Origem:** documento · **CF:** 0,8
- **SE:** Fumaça levemente azulada no escapamento
- **ENTÃO diagnóstico =** Motor queimando óleo (anéis de segmento ou retentores de válvula)
- **Explicação:** A fumaça azulada indica óleo lubrificante chegando à câmara de combustão.
- **Possíveis causas:** Anéis de segmento desgastados; Retentores de válvula desgastados
- **Recomendações (complementares):** Medir a compressão dos cilindros; Acompanhar o consumo de óleo; Avaliar retífica ou troca de retentores
- **Especialista indicado:** Mecânico de motor e câmbio

### R07 — Desgaste no kit de embreagem ou fluido do atuador baixo

- **Tipo:** diagnostico · **Origem:** documento · **CF:** 0,85
- **SE:** Marcha arranhando para entrar **E** Pedal de embreagem baixo
- **ENTÃO diagnóstico =** Desgaste no kit de embreagem ou fluido do atuador baixo
- **Explicação:** Marcha arranhando com pedal baixo sugere embreagem que não desacopla totalmente por desgaste ou perda de pressão hidráulica.
- **Possíveis causas:** Desgaste no kit de embreagem; Fluido do atuador baixo
- **Recomendações (complementares):** Verificar o nível do fluido do atuador; Inspecionar o kit de embreagem; Substituir o kit se houver desgaste
- **Especialista indicado:** Mecânico de motor e câmbio

### R08 — Junta do cabeçote queimada (água vazando para os cilindros)

- **Tipo:** diagnostico · **Origem:** documento · **CF:** 0,9
- **SE:** Fumaça branca espessa no escapamento **E** Reservatório de água abaixando
- **ENTÃO diagnóstico =** Junta do cabeçote queimada (água vazando para os cilindros)
- **Explicação:** Fumaça branca espessa com queda do nível de água indica líquido de arrefecimento entrando na câmara de combustão.
- **Possíveis causas:** Junta do cabeçote queimada
- **Recomendações (complementares):** Fazer teste de estanqueidade do sistema de arrefecimento; Verificar empenamento do cabeçote; Não rodar com o motor superaquecido
- **Especialista indicado:** Mecânico de motor e câmbio

## Freios

### R09 — Pastilhas de freio excessivamente gastas (atingiu o limitador)

- **Tipo:** diagnostico · **Origem:** documento · **CF:** 0,9
- **SE:** Ruído metálico agudo ao frear
- **ENTÃO diagnóstico =** Pastilhas de freio excessivamente gastas (atingiu o limitador)
- **Explicação:** O ruído agudo é emitido pelo limitador de desgaste, indicando que a pastilha chegou ao fim da vida útil.
- **Possíveis causas:** Pastilhas de freio excessivamente gastas
- **Recomendações (complementares):** Medir a espessura das pastilhas; Substituir as pastilhas; Inspecionar os discos
- **Especialista indicado:** Mecânico de freios

### R10 — Ar no sistema hidráulico ou vazamento de fluido de freio

- **Tipo:** diagnostico · **Origem:** documento · **CF:** 0,85
- **SE:** Pedal do freio esponjoso
- **ENTÃO diagnóstico =** Ar no sistema hidráulico ou vazamento de fluido de freio
- **Explicação:** Pedal esponjoso indica compressibilidade no circuito hidráulico, causada por ar ou perda de fluido.
- **Possíveis causas:** Ar no sistema hidráulico; Vazamento de fluido de freio
- **Recomendações (complementares):** Verificar o nível e vazamentos; Sangrar o sistema de freios; Evitar uso do veículo até a revisão
- **Especialista indicado:** Mecânico de freios

### R11 — Discos de freio empenados (necessita passe ou troca)

- **Tipo:** diagnostico · **Origem:** documento · **CF:** 0,85
- **SE:** Volante trepidando ao frear em alta velocidade
- **ENTÃO diagnóstico =** Discos de freio empenados (necessita passe ou troca)
- **Explicação:** A trepidação ao frear em alta velocidade é típica de variação de espessura ou empenamento dos discos.
- **Possíveis causas:** Discos de freio empenados
- **Recomendações (complementares):** Medir o empenamento dos discos; Retificar (passe) ou substituir os discos
- **Especialista indicado:** Mecânico de freios

### R12 — Sensor de velocidade de uma das rodas sujo ou cabo rompido

- **Tipo:** diagnostico · **Origem:** documento · **CF:** 0,85
- **SE:** Luz do ABS acesa **E** Frenagem normal, mas derrapa em freada brusca
- **ENTÃO diagnóstico =** Sensor de velocidade de uma das rodas sujo ou cabo rompido
- **Explicação:** Luz do ABS acesa com frenagem normal mas derrapagem em freada brusca indica que o ABS está inoperante por falta de sinal de uma roda.
- **Possíveis causas:** Sensor de velocidade da roda sujo; Cabo do sensor rompido
- **Recomendações (complementares):** Ler o código de falha do ABS; Limpar ou substituir o sensor da roda; Verificar o cabo do sensor
- **Especialista indicado:** Mecânico de freios

## Suspensão e Direção

### R13 — Alinhamento desregulado ou pressão irregular dos pneus

- **Tipo:** diagnostico · **Origem:** documento · **CF:** 0,8
- **SE:** Carro puxando fortemente para um lado
- **ENTÃO diagnóstico =** Alinhamento desregulado ou pressão irregular dos pneus
- **Explicação:** O desvio lateral em linha reta é típico de geometria desregulada ou diferença de calibragem.
- **Possíveis causas:** Alinhamento desregulado; Pressão irregular dos pneus
- **Recomendações (complementares):** Calibrar os pneus; Fazer alinhamento e balanceamento
- **Especialista indicado:** Mecânico de suspensão e direção

### R14 — Bieletas desgastadas, buchas da bandeja ou amortecedor estourado

- **Tipo:** diagnostico · **Origem:** documento · **CF:** 0,75
- **SE:** Ruído seco (toc-toc) em lombadas e buracos
- **ENTÃO diagnóstico =** Bieletas desgastadas, buchas da bandeja ou amortecedor estourado
- **Explicação:** O ruído seco em irregularidades indica folga em componentes da suspensão.
- **Possíveis causas:** Bieletas desgastadas; Buchas da bandeja desgastadas; Amortecedor estourado
- **Recomendações (complementares):** Inspecionar bieletas, buchas e amortecedores no elevador; Substituir o componente com folga
- **Especialista indicado:** Mecânico de suspensão e direção

### R15 — Baixo nível de fluido de direção ou bomba hidráulica danificada

- **Tipo:** diagnostico · **Origem:** documento · **CF:** 0,85
- **SE:** Volante muito pesado ao manobrar **E** Zumbido na direção hidráulica
- **ENTÃO diagnóstico =** Baixo nível de fluido de direção ou bomba hidráulica danificada
- **Explicação:** Volante pesado com zumbido indica falta de assistência hidráulica por baixo nível de fluido ou bomba com defeito.
- **Possíveis causas:** Baixo nível de fluido de direção; Bomba hidráulica danificada
- **Recomendações (complementares):** Verificar o nível e vazamentos do fluido; Completar ou trocar o fluido; Testar a bomba da direção
- **Especialista indicado:** Mecânico de suspensão e direção

### R16 — Câmber negativo excessivo (necessário ajuste de cambagem)

- **Tipo:** diagnostico · **Origem:** documento · **CF:** 0,8
- **SE:** Pneus gastando nas bordas internas
- **ENTÃO diagnóstico =** Câmber negativo excessivo (necessário ajuste de cambagem)
- **Explicação:** Desgaste nas bordas internas dos pneus indica inclinação excessiva das rodas para dentro.
- **Possíveis causas:** Câmber negativo excessivo
- **Recomendações (complementares):** Fazer ajuste de cambagem; Verificar componentes de suspensão avariados
- **Especialista indicado:** Mecânico de suspensão e direção

## Arrefecimento e Ar-Condicionado

### R17 — Interruptor térmico ("cebolão") queimado ou relé da ventoinha com defeito

- **Tipo:** diagnostico · **Origem:** documento · **CF:** 0,85
- **SE:** Ponteiro de temperatura no vermelho **E** Ventoinha não liga
- **ENTÃO diagnóstico =** Interruptor térmico ("cebolão") queimado ou relé da ventoinha com defeito
- **Explicação:** Superaquecimento com ventoinha parada indica que o acionamento elétrico da ventoinha não está funcionando.
- **Possíveis causas:** Interruptor térmico (cebolão) queimado; Relé da ventoinha com defeito
- **Recomendações (complementares):** Desligar o motor para evitar danos; Testar o interruptor térmico e o relé; Substituir a peça defeituosa
- **Especialista indicado:** Técnico de arrefecimento e ar-condicionado

### R18 — Mangueira do radiador ressecada/furada ou selo do motor vazando

- **Tipo:** diagnostico · **Origem:** documento · **CF:** 0,8
- **SE:** Poça de líquido colorido sob o motor
- **ENTÃO diagnóstico =** Mangueira do radiador ressecada/furada ou selo do motor vazando
- **Explicação:** Líquido de arrefecimento colorido no chão indica vazamento no circuito.
- **Possíveis causas:** Mangueira do radiador ressecada ou furada; Selo do motor vazando
- **Recomendações (complementares):** Localizar o ponto de vazamento; Substituir a mangueira ou o selo; Completar o líquido de arrefecimento
- **Especialista indicado:** Técnico de arrefecimento e ar-condicionado

### R19 — Vazamento de gás refrigerante no sistema

- **Tipo:** diagnostico · **Origem:** documento · **CF:** 0,85
- **SE:** Ar-condicionado só venta, não gela **E** Compressor do ar arma normalmente
- **ENTÃO diagnóstico =** Vazamento de gás refrigerante no sistema
- **Explicação:** Com o compressor armando normalmente, a falta de resfriamento indica perda de gás refrigerante.
- **Possíveis causas:** Vazamento de gás refrigerante
- **Recomendações (complementares):** Fazer teste de estanqueidade; Reparar o vazamento e recarregar o gás
- **Especialista indicado:** Técnico de arrefecimento e ar-condicionado

### R20 — Vazamento no radiador do ar quente interno (painel)

- **Tipo:** diagnostico · **Origem:** documento · **CF:** 0,9
- **SE:** Cheiro doce forte na cabine **E** Tapete úmido na parte da frente
- **ENTÃO diagnóstico =** Vazamento no radiador do ar quente interno (painel)
- **Explicação:** Cheiro doce e tapete úmido na frente indicam líquido de arrefecimento vazando dentro da cabine.
- **Possíveis causas:** Vazamento no radiador do ar quente interno
- **Recomendações (complementares):** Verificar o radiador do aquecedor atrás do painel; Substituir o radiador interno
- **Especialista indicado:** Técnico de arrefecimento e ar-condicionado

## Fatos

| Id | Descrição | Categoria | Tipo |
|---|---|---|---|
| `motor_nao_gira` | Motor não gira ao virar a chave | Elétrica e Ignição | booleano |
| `luzes_fracas` | Luzes do painel fracas | Elétrica e Ignição | booleano |
| `clique_ao_virar_chave` | Clique ao virar a chave | Elétrica e Ignição | booleano |
| `motor_gira_nao_pega` | Motor gira bem, mas não pega | Elétrica e Ignição | booleano |
| `luz_injecao_acesa` | Luz de injeção acesa | Elétrica e Ignição | booleano |
| `cheiro_queimado` | Cheiro de queimado | Elétrica e Ignição | booleano |
| `fumaca_painel` | Fumaça no painel | Elétrica e Ignição | booleano |
| `radio_luz_apagou` | Rádio ou luzes apagaram | Elétrica e Ignição | booleano |
| `bateria_nova_descarrega_rapido` | Bateria nova descarrega rápido | Elétrica e Ignição | booleano |
| `tensao_bateria` | Tensão medida na bateria (motor ligado) | Elétrica e Ignição | numerico |
| `motor_engasgando` | Carro engasgando na aceleração | Motor e Câmbio | booleano |
| `perda_potencia` | Perda de potência | Motor e Câmbio | booleano |
| `fumaca_azulada` | Fumaça levemente azulada no escapamento | Motor e Câmbio | booleano |
| `marcha_arranhando` | Marcha arranhando para entrar | Motor e Câmbio | booleano |
| `pedal_embreagem_baixo` | Pedal de embreagem baixo | Motor e Câmbio | booleano |
| `fumaca_branca_espessa` | Fumaça branca espessa no escapamento | Motor e Câmbio | booleano |
| `reservatorio_agua_abaixando` | Reservatório de água abaixando | Motor e Câmbio | booleano |
| `ruido_metalico_freio` | Ruído metálico agudo ao frear | Freios | booleano |
| `pedal_freio_esponjoso` | Pedal do freio esponjoso | Freios | booleano |
| `volante_trepida_frenagem` | Volante trepidando ao frear em alta velocidade | Freios | booleano |
| `luz_abs_acesa` | Luz do ABS acesa | Freios | booleano |
| `frenagem_normal_derrapa` | Frenagem normal, mas derrapa em freada brusca | Freios | booleano |
| `puxando_para_um_lado` | Carro puxando fortemente para um lado | Suspensão e Direção | booleano |
| `ruido_toc_toc` | Ruído seco (toc-toc) em lombadas e buracos | Suspensão e Direção | booleano |
| `volante_pesado` | Volante muito pesado ao manobrar | Suspensão e Direção | booleano |
| `zumbido_direcao` | Zumbido na direção hidráulica | Suspensão e Direção | booleano |
| `pneus_desgaste_interno` | Pneus gastando nas bordas internas | Suspensão e Direção | booleano |
| `temperatura_vermelho` | Ponteiro de temperatura no vermelho | Arrefecimento e Ar-Condicionado | booleano |
| `ventoinha_nao_liga` | Ventoinha não liga | Arrefecimento e Ar-Condicionado | booleano |
| `poca_liquido_colorido` | Poça de líquido colorido sob o motor | Arrefecimento e Ar-Condicionado | booleano |
| `ar_so_venta_nao_gela` | Ar-condicionado só venta, não gela | Arrefecimento e Ar-Condicionado | booleano |
| `compressor_arma_normal` | Compressor do ar arma normalmente | Arrefecimento e Ar-Condicionado | booleano |
| `cheiro_doce_cabine` | Cheiro doce forte na cabine | Arrefecimento e Ar-Condicionado | booleano |
| `tapete_umido_frente` | Tapete úmido na parte da frente | Arrefecimento e Ar-Condicionado | booleano |
| `tensao_abaixo_13_5` | Tensão da bateria abaixo de 13,5 V (fato derivado) | Elétrica e Ignição | derivado |
