import discord
from discord.ext import commands
import traceback
import settings
import utils
import mysql.connector
import sql_queries

logger = settings.logging.getLogger("bot")

#Connect to SQL Database
db_connection = mysql.connector.connect(
    host=settings.MYSQL_HOST,
    user=settings.MYSQL_USER,
    password=settings.MYSQL_PASSWORD,
    database=settings.MYSQL_DATABASE
)
db_cursor = db_connection.cursor()

#User Report Chat Command
class ReportModal(discord.ui.Modal, title="Create a user report"):

    username = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Username",
        required=True,
        placeholder="Enter the user's display name."
    )

    userid = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="UserID",
        required=True,
        placeholder="Enter the user's UserID."
    )

    reason = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Reason",
        required=True,
        placeholder="What is the reason for the report?"
    )

    evidence = discord.ui.TextInput(
        style=discord.TextStyle.long,
        label="Evidence",
        required=True,
        max_length=255,
        placeholder="Please describe evidence. If the evidence is "
    )

    action = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Action",
        required=True,
        placeholder="What action was taken?"
    )


    #Once the user has filled out the form, submit the data to the database, and post the log in the designated discord channel.
    async def on_submit(self, interaction: discord.Interaction):
        """This is my summary

        Args:
            interaction (discord.Interaction): Default discordpy Interaction
        """
        channel = interaction.guild.get_channel(settings.FEEDBACK_CH)

        embed = discord.Embed(title="Report",
                              color=discord.Color.red())
        embed.add_field(name="Username", value=self.username.value, inline=False)
        embed.add_field(name="UserID", value=self.userid.value, inline=False)
        embed.add_field(name="Reason", value=self.reason.value, inline=False)
        embed.add_field(name="Evidence", value=self.evidence.value, inline=False)
        embed.add_field(name="Action", value=self.action.value, inline=False)

        await channel.send(embed=embed)

        try:
            # Check if the user already exists in the users table
            db_cursor.execute(sql_queries.select_user_by_discord_id(), (self.userid.value,))
            existing_user_id = db_cursor.fetchone()

            # If the user doesn't exist, insert them into the users table
            if not existing_user_id:
                db_cursor.execute(sql_queries.insert_user(), (self.username.value, self.userid.value))
                db_connection.commit()

            # Check if the reason already exists in the reason table
            db_cursor.execute(sql_queries.select_reason_by_name(), (self.reason.value,))
            existing_reason_id = db_cursor.fetchone()

            # If the reason doesn't exist, insert them into the reason table
            if not existing_reason_id:
                db_cursor.execute(sql_queries.insert_reason(), (self.reason.value,))
                db_connection.commit()

            # Check if the punishment already exists in the punish table
            db_cursor.execute(sql_queries.select_punish_by_name(), (self.action.value,))
            existing_punish_id = db_cursor.fetchone()

            # If the punishment doesn't exist, insert them into the punish table
            if not existing_punish_id:
                db_cursor.execute(sql_queries.insert_punish(), (self.action.value,))
                db_connection.commit()               

        except mysql.connector.Error as err:
            print(f"MySQL Error: {err}")

        if sql_queries.create_log(db_cursor, db_connection, self.userid.value, self.reason.value, self.action.value):
            await interaction.response.send_message(f"Thank you. Your report has been received.", ephemeral=True)
        else:
            await interaction.response.send_message(f"An error occurred while creating the log entry.", ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error : Exception):
        traceback.print_tb(error.__traceback__)

def run():
    intents = discord.Intents.all()

    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        bot.tree.copy_global_to(guild=settings.GUILDS_ID)
        await bot.tree.sync(guild=settings.GUILDS_ID)
        await utils.load_videocmds(bot)

    @bot.tree.command()
    async def report(interaction: discord.Interaction):
        required_roles = ["Trial Moderator", "Moderator", "Senior Moderator", "Developer"]

        # Get the user who invoked the interaction
        user = interaction.user

        # Fetch the member object of the user
        member = interaction.guild.get_member(user.id)

        user_roles = [role.name for role in member.roles]
        if any(role in required_roles for role in user_roles):
            report_modal = ReportModal()
            report_modal.user = interaction.user
            await interaction.response.send_modal(report_modal)
        else:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)


    bot.run(settings.DISCORD_API_SECRET, root_logger=True)

if __name__ == "__main__":
    run()