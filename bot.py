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

@bot.event
async def on_ready():
    print(f"✅ Le bot est connecté en tant que {bot.user} (ID: {bot.user.id})")

    # Afficher les commandes chargées
    print("📌 Commandes disponibles :")
    for command in bot.commands:
        print(f"- {command.name}")

    try:
        # Synchroniser les commandes avec Discord
        synced = await bot.tree.sync()  # Synchronisation des commandes slash
        print(f"✅ Commandes slash synchronisées : {[cmd.name for cmd in synced]}")
    except Exception as e:
        print(f"❌ Erreur de synchronisation des commandes slash : {e}")

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


private_threads = {}  # Stocke les fils privés des nouveaux membres

class GuideView(View):
    def __init__(self, thread):
        super().__init__()
        self.thread = thread
        self.message_sent = False  # Variable pour contrôler l'envoi du message

    @discord.ui.button(label="📘 Guide", style=discord.ButtonStyle.success, custom_id="guide_button_unique")
    async def guide(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.message_sent:  # Empêche l'envoi du message en doublon
            await interaction.response.defer()
            await start_tutorial(self.thread, interaction.user)
            self.message_sent = True

    @discord.ui.button(label="❌ Non merci", style=discord.ButtonStyle.danger, custom_id="no_guide_button_unique")
    async def no_guide(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 Fermeture du fil...", ephemeral=True)
        await asyncio.sleep(2)
        await self.thread.delete()

class NextStepView(View):
    def __init__(self, thread):
        super().__init__()
        self.thread = thread

    @discord.ui.button(label="➡️ Passer à la suite", style=discord.ButtonStyle.primary, custom_id="next_button")
    async def next_step(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        # Récupérer l'utilisateur à partir du thread
        user = interaction.user  # interaction.user est l'utilisateur qui a cliqué
        # Envoie l'embed des informations économiques
        await send_economy_info(user)

async def wait_for_command(thread, user, command):
    def check(msg):
        return msg.channel == thread and msg.author == user and msg.content.startswith(command)

    await thread.send(f"🕒 En attente de `{command}`...")  # Envoi du message d'attente
    await bot.wait_for("message", check=check)  # Attente du message de la commande
    await thread.send("✅ Commande exécutée ! Passons à la suite. 🚀")  # Confirmation après la commande
    await asyncio.sleep(2)  # Pause avant de passer à l'étape suivante

async def start_tutorial(thread, user):
    tutorial_steps = [
        ("💼 **Commande Travail**", "Utilise `!!work` pour gagner un salaire régulièrement !", "!!work"),
        ("💃 **Commande Slut**", "Avec `!!slut`, tente de gagner de l'argent... Mais attention aux risques !", "!!slut"),
        ("🔫 **Commande Crime**", "Besoin de plus de frissons ? `!!crime` te plonge dans des activités illégales !", "!!crime"),
        ("🌿 **Commande Collecte**", "Avec `!!collect`, tu peux ramasser des ressources utiles !", "!!collect"),
        ("📊 **Classement**", "Découvre qui a le plus d'argent en cash avec `!!lb -cash` !", "!!lb -cash"),
        ("🕵️ **Voler un joueur**", "Tente de dérober l'argent d'un autre avec `!!rob @user` !", "!!rob"),
        ("🏦 **Dépôt Bancaire**", "Pense à sécuriser ton argent avec `!!dep all` !", "!!dep all"),
        ("💰 **Solde Bancaire**", "Vérifie ton argent avec `!!bal` !", "!!bal"),
    ]

    for title, desc, cmd in tutorial_steps:
        embed = discord.Embed(title=title, description=desc, color=discord.Color.blue())
        await thread.send(embed=embed)
        await wait_for_command(thread, user, cmd)  # Attente de la commande de l'utilisateur

    # Embed final des jeux
    games_embed = discord.Embed(
        title="🎲 **Autres Commandes de Jeux**",
        description="Découvre encore plus de moyens de t'amuser et gagner des Ezryn Coins !",
        color=discord.Color.gold()
    )
    games_embed.add_field(name="🪙 Pile ou Face", value="`!!cf` - Joue à pile ou face !", inline=False)
    games_embed.add_field(name="🃏 Blackjack", value="`!!bj` - Affronte le croupier dans un Blackjack !", inline=False)
    games_embed.add_field(name="💀 Smash", value="`!!sm` - Tente un jeu risqué !", inline=False)
    games_embed.add_field(name="🔫 Roulette Russe", value="`!!rr` - Joue avec le destin !", inline=False)
    games_embed.add_field(name="🎡 Roulette", value="`!!roulette` - Fais tourner la roue de la fortune !", inline=False)
    games_embed.set_footer(text="Amuse-toi bien sur Etherya ! 🚀")

    await thread.send(embed=games_embed)
    await thread.send("Clique sur **Passer à la suite** pour découvrir les systes impressionant de notre Economie !", view=NextStepView(thread))

class NextStepView(View):
            def __init__(self, thread):
                super().__init__()
                self.thread = thread

            @discord.ui.button(label="➡️ Passer à la suite", style=discord.ButtonStyle.primary, custom_id="next_button")
            async def next_step(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                user = interaction.user

                # Envoi du message privé
                await send_economy_info(user)

                # Envoi du message de confirmation dans le fil privé
                await self.thread.send("📩 Les détails de cette étape ont été envoyés en message privé.")

                # Attente de 2 secondes
                await asyncio.sleep(2)

                # Message d'avertissement avant suppression
                await self.thread.send("🗑️ Ce fil sera supprimé dans quelques instants.")

                # Suppression du fil privé
                await asyncio.sleep(3)
                await self.thread.delete()

async def send_economy_info(user: discord.Member):
            try:
                economy_embed = discord.Embed(
                    title="📌 **Lis ces salons pour optimiser tes gains !**",
                    description=(
                        "Bienvenue dans l'économie du serveur ! Pour en tirer le meilleur profit, assure-toi de lire ces salons :\n\n"
                        "💰 **Comment accéder à l'economie ?**\n➜ <#1344418391544303627>\n\n"
                        "📖 **Informations générales**\n➜ <#1340402373708746802>\n\n"
                        "💰 **Comment gagner des Coins ?**\n➜ <#1340402729272737926>\n\n"
                        "🏦 **Banque de l'Éco 1**\n➜ <#1340403431923519489>\n\n"
                        "🏦 **Banque de l'Éco 2**\n➜ <#1344309260825133100>\n\n"
                        "🎟️ **Ticket Finances** *(Pose tes questions ici !)*\n➜ <#1340443101386379486>\n\n"
                        "📈 **Astuce :** Plus tu en sais, plus tu gagnes ! Alors prends quelques minutes pour lire ces infos. 🚀"
                    ),
                    color=discord.Color.gold()
                )
                economy_embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1168755764760559637.webp?size=96&quality=lossless")
                economy_embed.set_footer(text="Bon jeu et bons profits ! 💰")

                dm_channel = await user.create_dm()
                await dm_channel.send(embed=economy_embed)
            except discord.Forbidden:
                print(f"Impossible d'envoyer un MP à {user.name} ({user.id})")

@bot.event
async def on_member_join(member):
    channel_id = 1342179655263977492  # Remplace par l'ID du salon souhaité
    channel = bot.get_channel(channel_id)

    if channel and isinstance(channel, discord.TextChannel):
        thread = await channel.create_thread(name=f"🎉 Bienvenue {member.name} !", type=discord.ChannelType.private_thread)
        await thread.add_user(member)
        private_threads[member.id] = thread

        # Embed de bienvenue
        welcome_embed = discord.Embed(
            title="🌌 Bienvenue à Etherya !",
            description=( 
                "Une aventure unique t'attend, entre **économie dynamique**, **stratégies** et **opportunités**. "
                "Prêt à découvrir tout ce que le serveur a à offrir ?"
            ),
            color=discord.Color.blue()
        )
        welcome_embed.set_thumbnail(url=member.avatar.url if member.avatar else bot.user.avatar.url)
        await thread.send(embed=welcome_embed)

        # Embed du guide
        guide_embed = discord.Embed(
            title="📖 Besoin d'un Guide ?",
            description=( 
                "Nous avons préparé un **Guide de l'Économie** pour t'aider à comprendre notre système monétaire et "
                "les différentes façons d'évoluer. Veux-tu le suivre ?"
            ),
            color=discord.Color.gold()
        )
        guide_embed.set_footer(text="Tu peux toujours y accéder plus tard via la commande /guide ! 🚀")
        await thread.send(embed=guide_embed, view=GuideView(thread))  # Envoie le guide immédiatement

@bot.tree.command(name="guide", description="Ouvre un guide personnalisé pour comprendre l'économie du serveur.")
async def guide_command(interaction: discord.Interaction):
    user = interaction.user

    # Crée un nouveau thread privé à chaque commande
    channel_id = 1342179655263977492
    channel = bot.get_channel(channel_id)

    if not channel:
        await interaction.response.send_message("❌ Le canal est introuvable ou le bot n'a pas accès à ce salon.", ephemeral=True)
        return

    # Vérifie si le bot peut créer des threads dans ce canal
    if not channel.permissions_for(channel.guild.me).send_messages or not channel.permissions_for(channel.guild.me).manage_threads:
        await interaction.response.send_message("❌ Le bot n'a pas les permissions nécessaires pour créer des threads dans ce canal.", ephemeral=True)
        return

    try:
        # Crée un nouveau thread à chaque fois que la commande est exécutée
        thread = await channel.create_thread(
            name=f"🎉 Bienvenue {user.name} !", 
            type=discord.ChannelType.private_thread,
            invitable=True
        )
        await thread.add_user(user)  # Ajoute l'utilisateur au thread

        # Embed de bienvenue et guide pour un nouveau thread
        welcome_embed = discord.Embed(
            title="🌌 Bienvenue à Etherya !",
            description="Une aventure unique t'attend, entre **économie dynamique**, **stratégies** et **opportunités**. "
                        "Prêt à découvrir tout ce que le serveur a à offrir ?",
            color=discord.Color.blue()
        )
        welcome_embed.set_thumbnail(url=user.avatar.url if user.avatar else bot.user.avatar.url)
        await thread.send(embed=welcome_embed)

    except discord.errors.Forbidden:
        await interaction.response.send_message("❌ Le bot n'a pas les permissions nécessaires pour créer un thread privé dans ce canal.", ephemeral=True)
        return

    # Embed du guide
    guide_embed = discord.Embed(
        title="📖 Besoin d'un Guide ?",
        description="Nous avons préparé un **Guide de l'Économie** pour t'aider à comprendre notre système monétaire et "
                    "les différentes façons d'évoluer. Veux-tu le suivre ?",
        color=discord.Color.gold()
    )
    guide_embed.set_footer(text="Tu peux toujours y accéder plus tard via cette commande ! 🚀")
    await thread.send(embed=guide_embed, view=GuideView(thread))  # Envoie le guide avec les boutons

    await interaction.response.send_message("📩 Ton guide personnalisé a été ouvert.", ephemeral=True)

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
