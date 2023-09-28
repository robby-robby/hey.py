function prompts {
  local port=8000
  (
    while ! nc -z localhost ${port}; do sleep 1; done
    open "http://localhost:${port}/prompts.html"
  ) &
  cd ~/.hey_py
  npx serve --cors -L -p ${port}
}
