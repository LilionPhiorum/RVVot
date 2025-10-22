import rvvot

tree=rvvot.tree

#試験用コマンド
#===============================================================
@tree.command(name="test",description="応答ありの関数のテスト")
async def tester(interaction:rvvot.discord.Interaction):
    await rvvot.hidden_response(interaction,"-..-")
    await interaction.response.send_message(not rvvot.is_user_talking(interaction))
#===============================================================