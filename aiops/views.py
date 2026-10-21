from django.shortcuts import render

from accounts.decorators import role_required
from accounts.models import User

ai_engineer_required = role_required(User.Role.AI_ENGINEER)


@ai_engineer_required
def index(request):
    """AI operations workspace. No AI services are connected yet."""
    return render(request, "aiops/index.html")
