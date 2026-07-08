# Informations textuelles

Cette extension fournit aux utilisateurs des informations contextuelles, adaptées à une grande variété d'usages.
En un seul appui de touche, elle peut vous donner la définition d'un mot, géolocaliser une adresse IP et vous renseigner sur un livre (via ISBN). Sélectionnez simplement quelque chose, utilisez le raccourci attribué et attendez.

## Services pris en charge

Actuellement, les fonctionnalités suivantes sont prises en charge :

* Informations sur les adresses IP. Comprend la géolocalisation, le FAI, l'identification des nœuds de sortie VPN/Tor et des réseaux cellulaires.
* Définitions de dictionnaire anglais, catégorie grammaticale, exemples de phrases, synonymes, antonymes, etc. Avec l'aimable contribution de la [Free Dictionary API](https://dictionaryapi.dev/)
* Recherche ISBN via l'API Google Books
* Vérification du type de carte bancaire (Mastercard, Visa, Discover, Amex, etc.)

L'extension prend également en charge la reconnaissance des numéros de téléphone et des adresses e-mail, bien qu'aucune information réelle ne soit récupérée. Cela est susceptible de changer dès que je trouve une utilisation pour ceux-ci et une API simple répondant à nos spécifications.

Remarque : Des expressions régulières sont utilisées en coulisse pour vérifier les données. Cela signifie que les adresses e-mail et les numéros de carte ne quitteront jamais votre machine.

## Raccourcis clavier

Remarque : ces raccourcis supposent un clavier en disposition anglaise et peuvent ne pas fonctionner autrement. Si vous rencontrez un problème, essayez d'abord de les modifier dans le dialogue Gestes de commandes.

* NVDA+; (point-virgule) : fournit des informations basées sur le texte sélectionné
* NVDA+MAJ+; (point-virgule) : fournit des informations sur le texte dans le presse-papiers
* NVDA+contrôle+; (point-virgule) : énonce la dernière information rapportée. Appuyez deux fois rapidement pour l'afficher dans une boîte de dialogue navigable.

## Note concernant Python 3

Depuis la version 2019.3 de NVDA, toutes les extensions doivent être compatibles Python 3. Si vous utilisez pour une raison quelconque une version plus ancienne, [1.0](https://github.com/cartertemm/text_information/releases/download/1.0/textInformation-1.0.nvda-addon) est la dernière version utilisable avec Python 2, et les définitions de dictionnaire ne fonctionnent plus en raison de l'abandon du Princeton WordnetWeb. Les deux doivent être considérées comme non prises en charge.

## Contribuer

Les contributions sont appréciées. Vous pouvez soit soumettre une PR, soit prendre contact via les informations suivantes :

twitter : @cartertemm

e-mail : cartertemm (at) gmail (dot) com

## Licence

Ce paquet est distribué selon les termes de la Licence Publique Générale GNU, version 2 ou ultérieure. Veuillez consulter le fichier COPYING.txt pour plus de détails.
