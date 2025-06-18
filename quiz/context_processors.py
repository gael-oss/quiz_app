from django.contrib import messages

def messages_json(request):
    """
    Fournit une liste JSON-serializable des messages pour json_script.
    """
    return {
        'messages_data': [
            {'message': m.message, 'tags': m.tags}
            for m in messages.get_messages(request)
        ]
    }
def roles(request):
    """
    Injecte deux flags au template :
      - is_teacher : True si l’utilisateur est dans le groupe 'Enseignant'
      - is_student : True si l’utilisateur est dans le groupe 'Etudiant'
    """
    user = request.user
    return {
        'is_teacher': user.is_authenticated and user.groups.filter(name='Enseignant').exists(),
        'is_student': user.is_authenticated and user.groups.filter(name='Etudiant').exists(),
    }
