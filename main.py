import discord
import config
from discord import app_commands
from typing import Literal
from botFunctionality import *

def main():
    client = MyClient(config.guildId)
    gSheet = Sheet.getState(config.credentials, config.sheetName)
    embedFactory = Embeds()
    
    @client.tree.command(description="Get all data")
    async def getall(interaction: discord.Interaction):
        if DefaultView.instance:
            try:
                foundMessage = await interaction.channel.fetch_message(DefaultView.messageId)
                return await interaction.response.send_message(f'There is already an active instance in #{foundMessage.channel} channel. ⚠️', ephemeral=True, delete_after=15)
            except Exception as err:
                print(err)
                DefaultView.instance = None

        try:        
            data = gSheet.getAllData()
        except Exception as err:
            print(err)
            return await interaction.response.send_message('Unable to receive spreadsheet data. ❌', ephemeral=True, delete_after=30)

        await interaction.response.send_message('Displaying data. ✅', ephemeral=True, delete_after=5)
        
        title, currentPage, currentIndex, itemsPerPage = "All Problems", 1, 0, 5
        displayView = DefaultView.getState(gSheet, embedFactory, data, title, currentPage, currentIndex, itemsPerPage)
        embed = embedFactory.createDataEmbed(data, title, currentPage, currentIndex, itemsPerPage)
        displayedMessage = await interaction.channel.send(embed=embed, view=displayView)
        DefaultView.messageId = displayedMessage.id
        timeout = await displayView.wait()
        if timeout:
            await displayedMessage.delete()
    
    @client.tree.command(description="Filter data by topic")
    @app_commands.describe(topic="Problem topic")
    async def gettopic(interaction: discord.Interaction, topic: Literal['Arrays', '2-Pointer', 'Stack', 'Binary Search', 'Sliding Window', 'Linked List', 'Trees', 'Tries', 'Heap', 'Intervals', 'Greedy', 'Backtracking', 'Graphs', '1D-DP', '2D-DP', 'Bit Manipulation', 'Math']):
        if TopicView.instance:
            try:
                foundMessage = await interaction.channel.fetch_message(TopicView.messageId)
                return await interaction.response.send_message(f'There is already an active instance in #{foundMessage.channel} channel. ⚠️', ephemeral=True, delete_after=15)
            except Exception as err:
                print(err)
                TopicView.instance = None

        try:        
            data = gSheet.filterByTopic(topic)
        except Exception as err:
            print(err)
            return await interaction.response.send_message('Unable to receive spreadsheet data. ❌', ephemeral=True, delete_after=30)

        if not data:
            return await interaction.response.send_message('There are no entries with this topic. ⚠️' , ephemeral=True, delete_after=15)

        await interaction.response.send_message('Displaying data. ✅', ephemeral=True, delete_after=5)
        
        currentPage, currentIndex, itemsPerPage = 1, 0, 5
        displayView = TopicView.getState(gSheet, embedFactory, data, topic, currentPage, currentIndex, itemsPerPage)
        embed = embedFactory.createDataEmbed(data, topic, currentPage, currentIndex, itemsPerPage)
        displayedMessage = await interaction.channel.send(embed=embed, view=displayView)
        TopicView.messageId = displayedMessage.id
        timeout = await displayView.wait()
        if timeout:
            await displayedMessage.delete()

    @client.tree.command(description="Create new entry")
    async def newentry(interaction: discord.Interaction):
        await interaction.response.send_modal(NewEntry(title="New Leetcode Entry", gSheet=gSheet))

    @client.tree.command(description="Update entry")
    @app_commands.describe(number="Problem number")
    async def updateentry(interaction: discord.Interaction, number: int):
        rowInformation = gSheet.getEntry(number)

        if not rowInformation:
            return await interaction.response.send_message(f'Problem #{number} could not be found. ⚠️', ephemeral=True, delete_after=15)

        rowNumber: int = rowInformation[0]
        rowData: list = rowInformation[1]
        problemInfo = str(rowData[0]) + ';' + rowData[1] + ';' + rowData[2]
        topic = str(rowData[3])
        solution = str(rowData[4])
        link = str(rowData[5])
        review = str(rowData[6])
        
        # Inject current entry's data into modal
        updateModal = UpdateEntry(title=f"Update Entry #{number}", gSheet=gSheet, rowNumber=rowNumber)
        updateModal.problemInfo.default = problemInfo
        updateModal.topic.default = topic
        updateModal.solution.default = solution
        updateModal.link.default = link
        updateModal.review.default = review

        await interaction.response.send_modal(updateModal)
    
    @client.tree.command(description="Delete entry")
    @app_commands.describe(number="Problem number")
    async def deleteentry(interaction: discord.Interaction, number: int):
        if gSheet.deleteEntry(number):
            return await interaction.response.send_message(f'Problem #{number} has been deleted. ✅', ephemeral=True, delete_after=15)
        else:
            return await interaction.response.send_message(f'Problem #{number} could not be deleted. ❌', ephemeral=True, delete_after=15)
        
    @client.tree.command(description="Help command => Displays all available commands.")
    async def help(interaction: discord.Interaction):
        embed = embedFactory.createHelpEmbed(config.commandsInfo)
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    client.run(config.token)

if __name__ == "__main__":
    main()