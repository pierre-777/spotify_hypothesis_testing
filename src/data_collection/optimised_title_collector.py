"""
Optimised Title Collector Module
Step 1: Collect Spotify track data for title complexity analysis

This module handles comprehensive data collection with balanced sampling
across genres, years, and title complexity metrics.
"""

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from pathlib import Path
import os
from datetime import datetime
import time
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimisedTitleCollector:
    """Collects Spotify track data with a focus on title analysis."""
    
    def __init__(self, test_mode: bool = False):
        """
        Initialize the collector.
        
        Args:
            test_mode (bool): If True, runs in test mode with reduced limits
        """
        self.test_mode = test_mode
        # 8 specific genres as requested
        self.genres = [
            "pop", "rock", "hip-hop", "electronic", 
            "jazz", "classical", "metal", "r&b"
        ]
        # Will be set properly in _setup_collection_parameters()
        self.target_per_genre = None
        self.max_retries = 3
        self.retry_delay = 1
        self._setup_spotify_client()
        self._setup_collection_parameters()
    
    def _setup_collection_parameters(self):
        """Setup collection parameters based on mode."""
        # Balanced temporal sampling parameters
        self.years = [2024, 2023, 2022, 2021, 2020]
        
        if self.test_mode:
            # Test mode: 2 tracks per year = 10 tracks per genre (~80 total)
            self.tracks_per_year = 2
            self.target_per_genre = 10
        else:
            # Full mode: 400 tracks per year = 2000 tracks per genre (~16,000 total)
            self.tracks_per_year = 400
            self.target_per_genre = 2000
    
    def set_collection_size(self, size: str):
        """
        Set collection size after initialization.
        
        Args:
            size (str): 'test', 'medium', 'full', or 'mega'
        """
        if size == 'test':
            self.tracks_per_year = 20  # 20 × 5 years = 100 per genre (~800 total)
            self.target_per_genre = 100
        elif size == 'medium':
            self.tracks_per_year = 50  # 50 × 5 years = 250 per genre (~2,000 total)
            self.target_per_genre = 250
        elif size == 'full':
            self.tracks_per_year = 800  # 800 × 5 years = 4000 per genre (~32,000 total)
            self.target_per_genre = 4000
        elif size == 'mega':
            self.tracks_per_year = 1200  # 1200 × 5 years = 6000 per genre (~48,000 total)
            self.target_per_genre = 6000
        else:
            raise ValueError("Size must be 'test', 'medium', 'full', or 'mega'")
        
        print(f"📊 Collection mode set to: {size}")
        print(f"   Tracks per year: {self.tracks_per_year}")
        print(f"   Target per genre: {self.target_per_genre}")
        print(f"   Expected total: ~{self.target_per_genre * len(self.genres):,}")

    def collect_tracks(self, target_per_genre: Optional[int] = None) -> Optional[pd.DataFrame]:
        """
        Collect tracks from Spotify API.
        
        Args:
            target_per_genre (int, optional): Override the default number of tracks per genre
            
        Returns:
            pd.DataFrame: Collected track data or None if collection fails
        """
        if target_per_genre is not None:
            # Override mode if specific target provided
            self.target_per_genre = target_per_genre
            # Calculate balanced tracks per year
            self.tracks_per_year = target_per_genre // len(self.years)
            if self.tracks_per_year == 0:
                self.tracks_per_year = 1  # Minimum 1 per year
        
        all_tracks = []
        total_tracks = 0
        
        mode_name = "�� TEST MODE" if self.tracks_per_year <= 20 else "🧪 MEDIUM MODE" if self.tracks_per_year <= 100 else "📥 FULL COLLECTION MODE" if self.tracks_per_year <= 800 else "🚀 MEGA COLLECTION MODE"
        print(f"\n{mode_name}")
        print(f"Target tracks per genre: {self.target_per_genre}")
        print(f"Balanced sampling: {self.tracks_per_year} tracks per year")
        print("-" * 40)
        
        try:
            for genre in self.genres:
                print(f"\nCollecting {genre} tracks...")
                genre_tracks = self._collect_genre_tracks(genre)
                
                if genre_tracks:
                    all_tracks.extend(genre_tracks)
                    total_tracks += len(genre_tracks)
                    
                    print(f"✅ Collected {len(genre_tracks)} {genre} tracks")
                    print(f"   Average popularity: {np.mean([t['popularity'] for t in genre_tracks]):.1f}")
                    print(f"   Average title length: {np.mean([len(t['track_name']) for t in genre_tracks]):.1f}")
                    
                    # Show artist diversity stats
                    unique_artists = len(set(t['artist_name'] for t in genre_tracks))
                    print(f"   Unique artists: {unique_artists}")
                    if len(genre_tracks) > 0:
                        avg_songs_per_artist = len(genre_tracks) / unique_artists
                        print(f"   Avg songs per artist: {avg_songs_per_artist:.1f}")
                else:
                    print(f"❌ Failed to collect {genre} tracks")
            
            if not all_tracks:
                print("\n❌ No tracks were collected")
                return None
                
            df = pd.DataFrame(all_tracks)
            
            # Add title analysis columns (if not already calculated)
            if 'title_length' not in df.columns:
                df['title_length'] = df['track_name'].str.len()
            if 'word_count' not in df.columns:
                df['word_count'] = df['track_name'].str.split().str.len()
            
            print(f"\n📊 Collection Summary:")
            print(f"Total tracks: {len(df):,}")
            print(f"Genres collected: {df['genre_category'].nunique()}")
            print(f"Average popularity: {df['popularity'].mean():.1f}")
            print(f"Average title length: {df['title_length'].mean():.1f}")
            print(f"Average word count: {df['word_count'].mean():.1f}")
            
            return df
            
        except Exception as e:
            print(f"\n❌ Collection failed: {e}")
        return None

    def _setup_spotify_client(self):
        # Initialize Spotify client
        client_credentials_manager = SpotifyClientCredentials(
            client_id=os.getenv('SPOTIPY_CLIENT_ID'),
            client_secret=os.getenv('SPOTIPY_CLIENT_SECRET')
        )
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        
        # Genre search strategies
        self.genre_categories = {
            'pop': [
                'genre:pop', 'genre:dance-pop', 'genre:synth-pop', 'genre:electropop',
                'genre:indie-pop', 'genre:teen-pop', 'genre:art-pop', 'genre:dream-pop',
                'genre:britpop', 'genre:k-pop', 'genre:j-pop'
            ],
            'rock': [
                'genre:rock', 'genre:alternative-rock', 'genre:indie-rock', 'genre:classic-rock',
                'genre:hard-rock', 'genre:post-rock', 'genre:progressive-rock', 'genre:psychedelic-rock',
                'genre:garage-rock', 'genre:punk-rock', 'genre:folk-rock'
            ],
            'hip-hop': [
                'genre:hip-hop', 'genre:rap', 'genre:trap', 'genre:old-school-hip-hop', 
                'genre:east-coast-hip-hop', 'genre:west-coast-hip-hop', 'genre:southern-hip-hop',
                'genre:conscious-hip-hop', 'genre:gangsta-rap'
            ],
            'electronic': [
                'genre:electronic', 'genre:techno', 'genre:house', 'genre:deep-house',
                'genre:tech-house', 'genre:progressive-house', 'genre:electro-house',
                'genre:trance', 'genre:dubstep', 'genre:drum-and-bass'
            ],
            'jazz': [
                'genre:jazz', 'genre:smooth-jazz', 'genre:jazz-fusion', 'genre:contemporary-jazz',
                'genre:bebop', 'genre:hard-bop', 'genre:cool-jazz', 'genre:free-jazz',
                'genre:latin-jazz', 'genre:swing'
            ],
            'classical': [
                'genre:classical', 'genre:baroque', 'genre:romantic', 'genre:contemporary-classical',
                'genre:classical-piano', 'genre:chamber-music', 'genre:orchestral', 'genre:opera'
            ],
            'metal': [
                'genre:metal', 'genre:heavy-metal', 'genre:death-metal', 'genre:black-metal',
                'genre:thrash-metal', 'genre:power-metal', 'genre:progressive-metal',
                'genre:doom-metal', 'genre:metalcore'
            ],
            'r&b': [
                'genre:r&b', 'genre:rnb', 'genre:contemporary-r&b', 'genre:neo-soul',
                'genre:alternative-r&b', 'genre:soul', 'genre:funk', 'genre:gospel'
            ]
        }
    
    def _collect_genre_tracks(self, genre: str) -> List[Dict]:
        """Collect tracks for a specific genre with balanced temporal sampling."""
        all_genre_tracks = []
        genre_queries = self.genre_categories[genre]
        
        print(f"Target tracks for {genre}: {self.target_per_genre}")
        print(f"Balanced sampling: {self.tracks_per_year} tracks per year")
        
        # Collect tracks per year
        for year in self.years:
            year_tracks = []
            print(f"\n  📅 Collecting {year} tracks (target: {self.tracks_per_year})...")
            
            query_index = 0
            attempts = 0
            max_attempts = len(genre_queries) * 3
            
            while len(year_tracks) < self.tracks_per_year and attempts < max_attempts:
                query = genre_queries[query_index % len(genre_queries)]
                
                search_queries = [
                    f"year:{year} {query}",
                    f"year:{year} genre:{genre}"
                ]
                
                for search_query in search_queries:
                    if len(year_tracks) >= self.tracks_per_year:
                        break
                        
                    tracks_found = self._search_tracks(
                        search_query, year_tracks, genre, year
                    )
                    
                    if tracks_found > 0:
                        print(f"    '{search_query}': +{tracks_found} tracks (total: {len(year_tracks)})")
                
                query_index += 1
                attempts += 1
            
            print(f"  ✅ {year}: Collected {len(year_tracks)} tracks")
            all_genre_tracks.extend(year_tracks)
        
        print(f"Final count for {genre}: {len(all_genre_tracks)} tracks")
        return all_genre_tracks
    
    def _search_tracks(self, search_query: str, year_tracks: List[Dict], 
                      genre: str, target_year: int) -> int:
        """Search for tracks with a specific query."""
        tracks_before = len(year_tracks)
        
        try:
            offset = 0
            max_offset = 500  # Reasonable limit
            
            while len(year_tracks) < self.tracks_per_year and offset < max_offset:
                try:
                    results = self.sp.search(
                        q=search_query,
                        type='track',
                        limit=50,
                        offset=offset
                    )
                    
                    tracks = results['tracks']['items']
                    if not tracks:
                        break
                    
                    for track in tracks:
                        if len(year_tracks) >= self.tracks_per_year:
                            break
                        
                        # Extract track info
                        track_name = track['name']
                        artist_name = track['artists'][0]['name']
                        
                        # Skip duplicates
                        if any(t['track_name'] == track_name and t['artist_name'] == artist_name 
                              for t in year_tracks):
                            continue
                        
                        # Verify release year
                        try:
                            album_date = track['album']['release_date']
                            if album_date:
                                release_year = int(album_date[:4])
                                if release_year != target_year:
                                    continue
                        except (ValueError, KeyError):
                            continue
                        
                        # Quality filters
                        popularity = track['popularity']
                        if popularity < 15:
                            continue
                        
                        # Calculate title features
                        title_length = len(track_name)
                        word_count = len(track_name.split())
                        has_numbers = any(c.isdigit() for c in track_name)
                        has_special_chars = any(not c.isalnum() and not c.isspace() for c in track_name)
                        
                        # Add the track
                        year_tracks.append({
                            'track_name': track_name,
                            'artist_name': artist_name,
                            'popularity': popularity,
                            'duration_ms': track['duration_ms'],
                            'title_length': title_length,
                            'word_count': word_count,
                            'has_numbers': has_numbers,
                            'has_special_chars': has_special_chars,
                            'genre_category': genre,
                            'release_year': target_year
                        })
                    
                    offset += len(tracks)
                    time.sleep(0.1)  # Rate limiting
                    
                except Exception as e:
                    print(f"    ❌ API error: {str(e)}")
                    break
        
        except Exception as e:
            print(f"    ❌ Search failed for {search_query}: {str(e)}")
        
        tracks_found = len(year_tracks) - tracks_before
        return tracks_found 