<script>
	let match_data = {
		score_a: 5,
		score_b: 13,
		map: 'Mirage'
	};

    let playerStats = [
        {name: "test", kills: 17, deaths: 12},
        {name: "test", kills: 17, deaths: 12},
        {name: "test", kills: 17, deaths: 12},
        {name: "test", kills: 17, deaths: 12},
        {name: "test", kills: 17, deaths: 12},
    ]
</script>

<div class="grid grid-cols-1 place-items-center pt-4">
	<div class="grid-rows-2">
		<p class="text-3xl upercase font-bold">
			{match_data.map}: {match_data.score_a} - {match_data.score_b}
		</p>
		<div class="table-container pt-4">
			<table class="table table-hover">
				<thead>
					<tr><th>Name</th><th>K/D</th><th>Kills</th><th>Deaths</th></tr>
				</thead>
                <tbody>
                    {#each playerStats as player, i}
                        <tr>
                            <td>{player.name}</td>
                            <td>{player.kills/player.deaths}</td>
                            <td>{player.kills}</td>
                            <td>{player.deaths}</td>
                        </tr>
                    {/each}
                </tbody>
			</table>
		</div>
	</div>
</div>
