monte uma api em python que receba modelos de blocos em csvs... 
a página deve ter uma lista dos csvs que subiram e um botão para carregar o dataframe. 
opcionalmente, deve haver um lugar para se carregar o dataframe do banco de dados que deu origem a aquele modelo de blocos;
depois de carregar o dataframe, ele deve  listar as variáveis e deve haver algum componente 
para especificar qual variável é a tonelagem ou volume. deve também listar variáveis e 
permitir mapear para teores e suas unidades no report. Também deve permitir selecionar entre 
as variáveis para apontar para categoria (litologia ou (recursos  e litologia)), com  o propósito 
de se reportar totais de tonelagem/volume, teores médios (podenderados por tonelagem se houver) 
discriminados pelas categorias. 
Deve aceitar também a entrada de um dicionário de cores para aplicar nos gráficos e dashboards. 
A página também deve produzir um relatório do dataframe com (deve haver opção para baixar o relatório: 
- quantidade de blocos discriminados por categoria (ou categorias);
- contagem de valores numéricos não nulos dos teores em gráfico de barras e tabela;
- no caso específico de fracionamento (g1, g2, g3, g4, ...gn): 
	- quantidade de valores numéricos, discriminados por categorias;
	- quantidade de valores iguais a 0 (100% passantes naquela malha);
- tabela de percentuais (em relação ao total de blocos daquela categoria), discriminados por categoria, 
dos blocos daquele teor que possuem valores naquela variável;
- tabela com totais de tonelagem ou volume (número inteiro com separador de milha em espaço ' ', e sem casas decimais), discriminados por categoria;
- se foi carregado o banco de dados, extrair mínimo e máximo do banco de dados, discriminados por categoria, 
e comparar se o mínimo do modelo de blocos (naquela categoria e naquele teor), não ficou inferior ao mínimo respectivo do banco de dados,
o que configuraria extrapolação (estimado fora do corredor dos valores de entrada). Da mesma forma isso deverá ser feito para os valores máximos.
a identificação de variáveis entre modelo de blocos e banco de dados não deve ser case sensitive;
o total de anomalias para mínimo e máximo deverá constar em tabela, discriminada por categoria e com opção de exportação para os blocos com anomalia;
- tabela com teores negativos, discriminada por categoria;
- tabela com estatística descritiva dos teores discriminada por categoria da densidade informada;

Crie uma sessão para dashboards:

- um como totais discriminados por categoria (litologia ou recurso e litologia caso a coluna recurso tenha sido oferecida), em treemap do plotly express;
- um gráfico de colunas discriminados por recurso, se houver coluna mapeada para recurso;
- gráfico de teor-tonelagem, (totais de tonelagem e teor médio dos blocos, restringindo-se por filtragem à medida que os teores são filtrados (teor de corte): uma linha para tonelagem e outra para teor, discriminada por lito;
- gráfico de histograma, interativamente podendo filtrar a litologia e o teor a ser visto;

- crie um arquivo instrucoes.md como memória de projeto;



 

