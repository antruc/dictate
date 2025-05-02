const onEvent = (type, listener) => {
  document.addEventListener(type, listener, false)
}

export default onEvent
