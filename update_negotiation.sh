#!/bin/bash
source .env
# Se placer dans le répertoire du référentiel Git
cd ./import

# Récupérer les changements à partir du référentiel distant
git fetch

# Vérifier s'il y a des mises à jour
if git diff --quiet HEAD origin/main; then
  echo "Aucune mise à jour disponible."
else
  echo "Mise à jour détectée. Exécution de git pull..."
  git pull

  # Exécuter le script Python s'il y a eu une mise à jour
  if [ $? -eq 0 ]; then
    echo "Exécution de la mise à jour ..."
    cd ..
    curl -s \
  --form-string "token=${PUSH_API}" \
  --form-string "user=${PUSH_USER}" \
  --form-string "message=New Ransoms chats have been added" \
  https://api.pushover.net/1/messages.json > /dev/null
  else
    echo "Erreur lors de la mise à jour du référentiel."
  fi
fi

