function confirmAction() {
    return userConfirmed = confirm('Are you sure you want to perform this action?');
}
// place in button:
// onclick = "return confirmAction();
// place in body:
// <script src="{% static 'scripts.js' %}></script>

