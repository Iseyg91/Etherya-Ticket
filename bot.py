import discord
from discord.ext import commands
from discord import app_commands
import os
import random
import asyncio
from keep_alive import keep_alive
from discord.ui import Button, View
from discord.ui import View, Select

token = os.environ['ETHERYA']
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True 
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix="+", intents=intents)

import discord
from discord.ext import commands
from discord import app_commands
import os
import random
import asyncio
from keep_alive import keep_alive
from discord.ui import Button, View
from discord.ui import View, Select

token = os.environ['ETHERYA']
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True 
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix="+", intents=intents)

OWNER_ID = 792755123587645461
STAFF_ROLE_ID = 1244339296706760726

# Lorsque le bot est prêt
@bot.event
async def on_ready():
    print(f"{bot.user} est connecté et prêt ! ✅")
    await bot.tree.sync()

@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")
    print(f"Commandes chargées: {list(bot.commands)}")  # Affiche les commandes disponibles

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    guild = message.guild
    member = guild.get_member(message.author.id)

    # Vérifier si la personne a le rôle à ignorer
    ignored_role_id = 1170326040485318686
    if any(role.id == ignored_role_id for role in member.roles):
        return

    # Vérifier si le message mentionne l'Owner
    if f"<@{OWNER_ID}>" in message.content:
        embed = discord.Embed(
            title="🔹 Hey, besoin d'aide ?",  
            description=(f"Salut {message.author.mention}, merci d’éviter de mentionner le Owner inutilement.\n\n"
                         "👥 **L'équipe d'administration est là pour répondre à tes questions et t’aider !**\n"
                         "📩 **Besoin d'aide ? Clique sur le bouton ci-dessous ou va dans <#1166093151589634078>.**"),
            color=0x00aaff  # Bleu cyan chill
        )
        embed.set_image(url="https://raw.githubusercontent.com/Cass64/EtheryaBot/refs/heads/main/images_etherya/etheryaBot_banniere.png") 
        if bot.user.avatar:
            embed.set_thumbnail(url=bot.user.avatar.url) 
        embed.add_field(name="❓ Pourquoi éviter de mentionner le Owner ?", 
                        value="Le Owner est souvent occupé avec la gestion du serveur. Pour une réponse rapide et efficace, passe par le support ou un admin ! 🚀", 
                        inline=False)
        embed.set_footer(text="Merci de ta compréhension • L'équipe d'administration", icon_url=bot.user.avatar.url)

        button = Button(label="📩 Ouvrir un ticket", style=discord.ButtonStyle.primary, url="https://discord.com/channels/1034007767050104892/1166093151589634078/1340663542335934488")
        view = View()
        view.add_item(button)
        await message.channel.send(embed=embed, view=view)

    # Permet au bot de continuer à traiter les commandes
    await bot.process_commands(message)

# IDs des rôles et de la catégorie
STAFF_ROLE_ID = 1165936153418006548
PANEL_ROLE_ID = 1170326040485318686  # Seul ce rôle peut utiliser /panel
CATEGORY_ID = 1166091020472160466

@bot.tree.command(name="panel", description="Créer un ticket personnalisé")
@app_commands.describe(
    panel_title="Titre du panel",
    panel_description="Description du panel",
    panel_image="URL de l'image du panel",
    ticket_title="Titre du ticket",
    ticket_description="Description du ticket",
    ticket_image="URL de l'image du ticket",
    emoji="Emoji à mettre devant le nom du ticket"
)
async def panel(interaction: discord.Interaction, panel_title: str, panel_description: str, panel_image: str,
                ticket_title: str, ticket_description: str, ticket_image: str, emoji: str):

    # Vérifier que l'utilisateur a le rôle nécessaire
    if PANEL_ROLE_ID not in [role.id for role in interaction.user.roles]:
        await interaction.response.send_message("❌ Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
        return

    button = discord.ui.Button(label="Ouvrir un ticket", style=discord.ButtonStyle.green)

    # Boutons Claim et Close
    claim_button = discord.ui.Button(label="📌 Claim", style=discord.ButtonStyle.blurple)
    close_button = discord.ui.Button(label="❌ Fermer", style=discord.ButtonStyle.red)

    async def ticket_callback(interaction: discord.Interaction):
        category = discord.utils.get(interaction.guild.categories, id=CATEGORY_ID)
        staff_role = interaction.guild.get_role(STAFF_ROLE_ID)

        if not category or not staff_role:
            await interaction.response.send_message("❌ Problème avec la catégorie ou le rôle Staff.", ephemeral=True)
            return

        # Création du nom du ticket avec l'emoji
        ticket_name = f"︱{emoji}・ticket-{interaction.user.name}"

        # Création du salon ticket
        ticket_channel = await interaction.guild.create_text_channel(
            name=ticket_name,
            category=category,
            overwrites={
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True),
                staff_role: discord.PermissionOverwrite(view_channel=True)
            }
        )

        # Envoi du message privé au membre pour confirmer la création du ticket
        try:
            await interaction.user.send(f"✅ Votre ticket a été créé avec succès ! Vous pouvez le retrouver ici : {ticket_channel.mention}")
        except discord.Forbidden:
            # Si le bot ne peut pas envoyer de message privé, on l'indique
            await interaction.response.send_message("❌ Je ne peux pas vous envoyer de message privé.", ephemeral=True)

        # Créer l'embed du ticket
        embed_ticket = discord.Embed(
            title=ticket_title,
            description=ticket_description,
            color=discord.Color.green()
        )
        embed_ticket.set_footer(text=f"Ticket ouvert par {interaction.user.name}")
        embed_ticket.set_image(url=ticket_image)

        # Créer la vue pour le ticket avec timeout=None
        view_ticket = discord.ui.View(timeout=None)  # Aucun timeout
        view_ticket.add_item(claim_button)
        view_ticket.add_item(close_button)

        # Envoi du message dans le salon du ticket
        await ticket_channel.send(f"{interaction.user.mention} | {staff_role.mention}", embed=embed_ticket, view=view_ticket)

        async def claim_callback(interaction: discord.Interaction):
            if STAFF_ROLE_ID not in [role.id for role in interaction.user.roles]:
                await interaction.response.send_message("❌ Vous n'avez pas la permission d'exécuter cette action.", ephemeral=True)
                return

            embed_claim = discord.Embed(
                title="Ticket en cours de traitement",
                description=f"📌 Ce ticket sera traité par {interaction.user.mention}",
                color=discord.Color.orange()
            )

            # Modifier les permissions pour afficher uniquement au staff qui claim
            await interaction.channel.set_permissions(interaction.guild.default_role, view_channel=False)
            await interaction.channel.set_permissions(interaction.user, view_channel=True)
            await interaction.channel.set_permissions(staff_role, view_channel=True)

            # Supprimer le bouton Claim
            view_ticket.remove_item(claim_button)
            await interaction.message.edit(view=view_ticket)

            await interaction.response.send_message(embed=embed_claim)

        async def close_callback(interaction: discord.Interaction):
            if STAFF_ROLE_ID not in [role.id for role in interaction.user.roles]:
                await interaction.response.send_message("❌ Vous n'avez pas la permission d'exécuter cette action.", ephemeral=True)
                return

            embed_closed = discord.Embed(
                title="Ticket fermé",
                description=f"🔒 Ce ticket a été fermé par {interaction.user.mention}",
                color=discord.Color.red()
            )

            reopen_button = discord.ui.Button(label="🔄 Réouvrir", style=discord.ButtonStyle.green)
            delete_button = discord.ui.Button(label="🗑 Supprimer", style=discord.ButtonStyle.gray)

            async def reopen_callback(interaction: discord.Interaction):
                if STAFF_ROLE_ID not in [role.id for role in interaction.user.roles]:
                    await interaction.response.send_message("❌ Vous n'avez pas la permission d'exécuter cette action.", ephemeral=True)
                    return

                await interaction.channel.set_permissions(interaction.guild.default_role, view_channel=False)
                await interaction.channel.set_permissions(interaction.user, view_channel=True)
                await interaction.channel.set_permissions(staff_role, view_channel=True)

                embed_reopened = discord.Embed(
                    title="Ticket réouvert",
                    description=f"✅ Le ticket a été réouvert par {interaction.user.mention}",
                    color=discord.Color.green()
                )
                await interaction.response.send_message(embed=embed_reopened)

            async def delete_callback(interaction: discord.Interaction):
                if STAFF_ROLE_ID not in [role.id for role in interaction.user.roles]:
                    await interaction.response.send_message("❌ Vous n'avez pas la permission d'exécuter cette action.", ephemeral=True)
                    return

                embed_delete = discord.Embed(
                    title="Suppression du ticket",
                    description="🗑 Ce ticket sera supprimé dans quelques instants...",
                    color=discord.Color.dark_gray()
                )
                await interaction.response.send_message(embed=embed_delete)
                await interaction.channel.delete()

            reopen_button.callback = reopen_callback
            delete_button.callback = delete_callback

            view_close = discord.ui.View(timeout=None)  # Aucun timeout pour cette vue
            view_close.add_item(reopen_button)
            view_close.add_item(delete_button)

            await interaction.response.send_message(embed=embed_closed)
            await interaction.channel.send(embed=embed_closed, view=view_close)

        claim_button.callback = claim_callback
        close_button.callback = close_callback

        view_ticket = discord.ui.View(timeout=None)  # Aucun timeout pour cette vue
        view_ticket.add_item(claim_button)
        view_ticket.add_item(close_button)

        embed_ticket = discord.Embed(
            title=ticket_title,
            description=ticket_description,
            color=discord.Color.green()
        )
        embed_ticket.set_footer(text=f"Ticket ouvert par {interaction.user.name}")
        embed_ticket.set_image(url=ticket_image)

    button.callback = ticket_callback
    view = discord.ui.View(timeout=None)  # Aucun timeout pour cette vue
    view.add_item(button)

    embed_panel = discord.Embed(
        title=panel_title,
        description=panel_description,
        color=discord.Color.blue()
    )
    embed_panel.set_image(url=panel_image)
    embed_panel.set_footer(text="Cliquez sur le bouton ci-dessous pour ouvrir un ticket")

    # Envoi du message avec le bouton pour ouvrir un ticket
    try:
        await interaction.response.send_message(embed=embed_panel, view=view)
    except discord.HTTPException:
        await interaction.response.send_message("❌ Une erreur est survenue lors de l'envoi du message.", ephemeral=True)

@bot.tree.command(name="transfer", description="Transférer un ticket à un autre staff")
async def transfer(interaction: discord.Interaction, member: discord.Member):
    # Vérifier si l'utilisateur a le rôle staff
    if STAFF_ROLE_ID not in [role.id for role in interaction.user.roles]:
        await interaction.response.send_message("❌ Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
        return

    # Vérifier que le membre spécifié est un staff
    if STAFF_ROLE_ID not in [role.id for role in member.roles]:
        await interaction.response.send_message("❌ Le membre spécifié n'est pas un staff.", ephemeral=True)
        return

    ticket_channel = interaction.channel
    embed_transfer = discord.Embed(
        title="Ticket transféré",
        description=f"✅ Le ticket a été transféré à {member.mention} par {interaction.user.mention}.",
        color=discord.Color.blue()
    )

    # Modifier les permissions du ticket pour permettre au nouveau staff de voir
    staff_role = interaction.guild.get_role(STAFF_ROLE_ID)
    await ticket_channel.set_permissions(member, view_channel=True)
    await interaction.response.send_message(embed=embed_transfer)  # Assure que c'est le seul message envoyé pour le transfert


# Token pour démarrer le bot (à partir des secrets)
# Lancer le bot avec ton token depuis l'environnement
keep_alive()
bot.run(token)
