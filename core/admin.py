from django.contrib import admin
import core.models
# Register your models here.

admin.site.register(core.models.League)
admin.site.register(core.models.Team)
admin.site.register(core.models.Player)
admin.site.register(core.models.UpcomingMatch)
admin.site.register(core.models.UserSquad)
admin.site.register(core.models.UserSquadPlayer)
admin.site.register(core.models.PlayedMatch)
admin.site.register(core.models.PlayerMatchStats)