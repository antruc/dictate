import onEvent from './onEvent.js'

const sender = {
  async sendText() {
    const textArea = document.querySelector('#textarea')
    const url = window.location.href
    if (textArea.value.length > 0) {
      try {
        await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'text/plain;charset=utf-8'
          },
          body: textArea.value
        })
        textArea.value = ''
      } catch (error) {
        if (error) {
          alert('Connection lost')
        }
      }
    }
  },
  buttonSend(event) {
    const matchButton = event.target.matches('#send')
    if (matchButton) {
      sender.sendText()
    }
  },
  autoSend(event) {
    const matchText = event.target.matches('#textarea')
    const checkbox = document.querySelector('#checkbox1')
    if (matchText) {
      if (checkbox.checked) {
        sender.sendText()
      }
    }
  },
  enableButton(event) {
    const matchCheckbox = event.target.matches('#checkbox1')
    const is_disabled = document.querySelector('#send').getAttribute('disabled')
    const sendButton = document.querySelector('#send')
    if (matchCheckbox) {
      if (is_disabled) {
        sendButton.removeAttribute('disabled')
      } else {
        sendButton.setAttribute('disabled', 'true')
      }
    }
  },
  isChecked() {
    const checkbox = document.querySelector('#checkbox1')
    const sendButton = document.querySelector('#send')
    if (!checkbox.checked) {
      checkbox.checked = true
    }
    sendButton.setAttribute('disabled', 'true')
  },
  uncaught() {
    window.addEventListener('unhandledrejection', () => {
      alert('Connection lost')
    })
  },
  init() {
    this.isChecked()
    onEvent('click', this.buttonSend)
    onEvent('input', this.autoSend)
    onEvent('click', this.enableButton)
    this.uncaught()
  }
}

export default sender
