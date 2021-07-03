import tokens           # Tokens to log in
import spotipy          # Spotify API
from spotipy.oauth2 import SpotifyOAuth
import tweepy           # Twitter API
import sched, time      # Daemon
import random           # Random


# Spotify API stuffs
PORT_NUMBER = 8080
SPOTIPY_REDIRECT_URI = 'http://localhost:8080'
SCOPE = 'user-read-playback-state'
CACHE = '.spotipyoauthcache'

# Initialize scheduler
s = sched.scheduler(time.time, time.sleep)
REFRESH_TIME_IN_SECONDS = 60

# Initialize Spotify API handler
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=tokens.spotify_client_id, client_secret=tokens.spotify_client_secret, redirect_uri=SPOTIPY_REDIRECT_URI, scope=SCOPE))

# Initialize Twitter authentication and API
twitter_auth = tweepy.OAuthHandler(tokens.twitter_api_key, tokens.twitter_api_secret_key)
twitter_auth.set_access_token(tokens.twitter_access_token, tokens.twitter_access_token_secret)
twitter_api = tweepy.API(twitter_auth)


# Main function
def run(last_played_song_uri):
        try:
                # Grab and store current Spotify playback
                playback_data = sp.current_playback()

                # Check if API returns viable data
                if playback_data != None:

                        # Check if last stored song is currently playing
                        if playback_data["item"]["uri"] == last_played_song_uri:

                                # Check if progress_ms is greater than current progress_ms. If so that means the song was repeated
                                # Actually scratch that I don't want duplicate tweets for now, I can handle it later if I want
                                1==1

                        else:
                                last_played_song_uri = playback_data["item"]["uri"]
                                tweet(playback_data)
        
        except:
                print("Error getting Spotify data.")
                
        # Restart the loop
        s.enter(REFRESH_TIME_IN_SECONDS,1,run, (last_played_song_uri,))


# Compile artists
def compile_artists(artists):
        output = []     # List of all artists

        # Loop through and append to output
        for artist in artists:
                output.append(artist["name"])

        # Return
        return ", ".join(output)


# Get playlist details (if any)
# If no playlist, return False
def get_playlist_details(playback_data_context):
        output = {}

        # Check if playback context is a playlist
        if playback_data_context["type"] == "playlist":

                # Get playlist data
                # URI formatted as spotify:playlist:6CGLC6SmVnbhM0LtgnmBpn, so
                # to get ID we need to split by : and get the third item
                playlist_data = sp.playlist(playback_data_context["uri"].split(":")[2])

                # Congregate data
                output["name"] = playlist_data["name"]
                output["author"] = playlist_data["owner"]["display_name"]
                output["link"] = playlist_data["external_urls"]["spotify"]

                # Return
                return output

        # Self-explanatory
        else:
                return False


# Tweet
def tweet(playback_data):

        # People emojis
        people = ["👨‍🎓","👩‍🎓","👨‍🌾","👩‍🌾","👨‍💼","👩‍💻","👩‍🎨","👩‍✈️","👨‍✈️","👨‍🎨","👨‍🚀","👰🏻‍♂️","👯‍♀️","🎅🏻","🦸‍♀️","🧚🏻‍♀️","🧜‍♀️","🧛🏻‍♂️","🧞‍♂️"]

        # Congregate data
        song = playback_data["item"]["name"]
        album = playback_data["item"]["album"]["name"]
        artists = compile_artists(playback_data["item"]["artists"])
        url = playback_data["item"]["external_urls"]["spotify"]
        progress_ms = playback_data["progress_ms"]

        # Attempt to get playlist data
        playlist_data = get_playlist_details(playback_data["context"])

        # Try
        try:
                # Tweet and save tweet
                music_info_tweet = twitter_api.update_status('({}) Gabe is now listening to\n🎵 {}\n💽 {}\n👨‍🎤 {}\n\n{}'.format(progress_ms, song, album, artists, url))

                # If there is playlist data
                if playlist_data != False:

                        # Reply to the original tweet
                        additional_info_tweet = twitter_api.update_status('This song is from a playlist\n🎧 {}\n{} {}\n\n{}'.format(playlist_data["name"], random.choice(people), playlist_data["author"], playlist_data["link"]), in_reply_to_status_id=music_info_tweet.id, auto_populate_reply_metadata=True)

        except:
                print('Error Tweeting.')



# Run the function on start, then start the loop
print("Program initialized.")
run("")
s.run()