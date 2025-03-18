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

    game = discord.Game("Etherya")
    await bot.change_presence(status=discord.Status.online, activity=game)
    print(f'{bot.user} est connecté !')

    # Afficher les commandes chargées
    print("📌 Commandes disponibles 😊")
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
    games_embed.add_field(name="🐔 Cock-Fight", value="`!!cf` - Combat de Poulet !", inline=False)
    games_embed.add_field(name="🃏 Blackjack", value="`!!bj` - Jeux de Carte !", inline=False)
    games_embed.add_field(name="🎰 Slot Machine", value="`!!sm` - Tente un jeu risqué !", inline=False)
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
# Token pour démarrer le bot (à partir des secrets)
# Lancer le bot avec ton token depuis l'environnement
keep_alive()
bot.run(token)
