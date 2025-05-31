import re
import pandas as pd
import nltk
import json
from prophet import Prophet
from collections import defaultdict
from datetime import datetime
from nltk.sentiment import SentimentIntensityAnalyzer

'''# Download necessary NLTK data
nltk.download('vader_lexicon')
nltk.download('punkt')
nltk.download('stopwords')  # <-- Add this line to fix the error
nltk.download('punkt_tab')'''

# Load data files
feedback_df = pd.read_csv('./content/customer_feedback.csv')
catalog_df = pd.read_csv('./content/product_catalog.csv')
sales_df = pd.read_csv('./content/sales_data.csv')
search_df = pd.read_csv('./content/search_trends.csv')

## =================================================================================
# Function to clean timestamps
def clean_timestamp(date_str):
	try:
		# Try parsing the date
		return pd.to_datetime(date_str, errors='coerce', format='%Y-%m-%d')
	except:
		return pd.NaT

# Apply cleaning
sales_df['timestamp'] = sales_df['timestamp'].apply(clean_timestamp)

# Drop rows with NaT (invalid dates)
sales_df = sales_df.dropna(subset=['timestamp']).reset_index(drop=True)

# Preview cleaned data
print("✅ Cleaned Sales Data:")
#display(sales_df.head())
## =================================================================================
# Function to clean comment text
def clean_text(text):
	if pd.isnull(text):
		return ""
	# Remove special characters and emojis
	text = re.sub(r'[^\w\s.,!?]', '', text)
	# Remove "Reviewed by..." pattern
	text = re.sub(r'\(Reviewed by.*?\)', '', text, flags=re.IGNORECASE)
	# Remove extra spaces
	text = re.sub(r'\s+', ' ', text).strip()
	return text

# Apply cleaning
feedback_df['cleaned_comment'] = feedback_df['commentText'].apply(clean_text)

# Preview cleaned comments
print("✅ Cleaned Feedback Data:")
#display(feedback_df[['commentText', 'cleaned_comment']].head())
## =================================================================================
# Merge Feedback + Product Catalog
merged_df = feedback_df.merge(catalog_df, on='productId', how='left')

# Aggregate Sales Data by Product + Month-Year
sales_df['timestamp'] = pd.to_datetime(sales_df['timestamp'])
sales_df['month_year'] = sales_df['timestamp'].dt.to_period('M').astype(str)
sales_agg = sales_df.groupby(['productId', 'month_year'])['quantitySold'].sum().reset_index()

# Add 'month_year' to feedback data for merge
merged_df['date'] = pd.to_datetime(merged_df['date'])
merged_df['month_year'] = merged_df['date'].dt.to_period('M').astype(str)

# Merge sales data
merged_df = merged_df.merge(sales_agg, on=['productId', 'month_year'], how='left')

# Fill missing sales with 0
merged_df['quantitySold'] = merged_df['quantitySold'].fillna(0)

# Preview merged data
print("✅ Merged Feedback + Catalog + Sales:")
#display(merged_df.head())
## =================================================================================
# Lowercase queries for matching
search_df['query'] = search_df['query'].str.lower()

# Add 'month_year' column
search_df['timestamp'] = pd.to_datetime(search_df['timestamp'])
search_df['month_year'] = search_df['timestamp'].dt.to_period('M').astype(str)

# Create a category mapping from product_catalog
catalog_keywords = catalog_df[['category', 'keywords']]
category_map = {}
for _, row in catalog_keywords.iterrows():
	for keyword in row['keywords'].split(','):
		category_map[keyword.strip().lower()] = row['category']

# Map queries to categories
def map_query_to_category(query):
	for keyword, category in category_map.items():
		if keyword in query:
			return category
	return 'Other'

search_df['category'] = search_df['query'].apply(map_query_to_category)

# Aggregate search frequency by category + month
search_agg = search_df.groupby(['category', 'month_year'])['frequency'].sum().reset_index()

# Preview
print("✅ Aggregated Search Trends:")
#display(search_agg.head())
## =================================================================================
# Merge search trends by category + month
merged_df = merged_df.merge(search_agg, on=['category', 'month_year'], how='left')

# Fill missing search frequency with 0
#merged_df['frequency'] = merged_df['frequency'].fillna(0)

# Final merged data preview
print("✅ Final Merged Data:")
#display(merged_df.head())
merged_df.to_csv('./content/sales_data_merged.csv', index=False)
## =================================================================================
## =================================================================================
## =================================================================================
## =================================================================================

class dataservices:

	@staticmethod
	def catalogue():
		# Select id, title, and category columns
		selected_df = catalog_df[['productId', 'title', 'category']]

		# Convert to JSON
		json_data = selected_df.to_json(orient='records', indent=4)

		return json_data

	@staticmethod
	def salesPrediction(productId=False):
		global sales_df
		df_filtered = sales_df.copy()
		if productId:
			df_filtered = df_filtered[df_filtered['productId'] == productId]

		# Aggregate monthly sales
		df_filtered['Month'] = df_filtered['timestamp'].dt.to_period('M').dt.to_timestamp()
		monthly_sales = df_filtered.groupby('Month')['quantitySold'].sum().reset_index()
		monthly_sales.columns = ['ds', 'y']  # Prophet requires 'ds' and 'y' columns

		# Fit Prophet model
		model = Prophet()
		model.fit(monthly_sales)

		# Forecast next 6 months
		last_date = monthly_sales['ds'].max()
		future = model.make_future_dataframe(periods=8, freq='MS')
		forecast = model.predict(future)

		# Separate past and future
		past_forecast = forecast[forecast['ds'] <= last_date]
		future_forecast = forecast[forecast['ds'] > last_date]

		# Format output as required
		past = {}
		for idx, row in past_forecast.iterrows():
			date_str = row['ds'].strftime('%Y-%m-%d')
			past[date_str] = int(row['yhat'])

		future = {}
		for idx, row in future_forecast.iterrows():
			date_str = row['ds'].strftime('%Y-%m-%d')
			tmp = int(row['yhat'])
			if tmp > 0:
				future[date_str] = tmp

		# Return as JSON
		output = {
			'past': past,
			'future': future
		}

		return json.dumps(output, indent=4)

	@staticmethod
	def sentiments():
		json_data = {}

		# Initialize VADER
		sia = SentimentIntensityAnalyzer()

		# Sentiment scores
		merged_df['sentiment_score'] = merged_df['cleaned_comment'].apply(lambda x: sia.polarity_scores(x)['compound'])
		sentiment_counts = merged_df['sentiment_score'].value_counts().reset_index()

		# Sentiment labels
		def label_sentiment(score):
			if score > 0.05:
				return 'Positive'
			elif score < -0.05:
				return 'Negative'
			else:
				return 'Neutral'

		merged_df['sentiment_label'] = merged_df['sentiment_score'].apply(label_sentiment)

		# Check results
		merged_df[['cleaned_comment', 'sentiment_score', 'sentiment_label']].head()
		sentiment_counts = merged_df['sentiment_label'].value_counts().reset_index()
		sentiment_counts.columns = ['sentiment_label', 'count']
		json_data['counts'] = sentiment_counts.to_json(orient='records')
		# ---------
		# Group data: average sentiment + total sales per product
		sales_sentiment = merged_df.groupby('productId').agg({
			'sentiment_score': 'mean',
			'quantitySold': 'sum'
		}).reset_index()

		# Rename columns for clarity
		sales_sentiment.columns = ['productId', 'avg_sentiment_score', 'total_sales']

		# Convert to JSON
		json_data['correlation'] = sales_sentiment.to_json(orient='records')
		# ---------
		return '{"counts": '+json_data['counts']+', "correlation": '+json_data['correlation']+'}'

	@staticmethod
	def opportunities():
		# Aggregate search frequency and sales by category
		trend_opportunity = merged_df.groupby('category').agg({
			'quantitySold': 'mean',
			'frequency': 'mean'
		}).reset_index()

		# Rename columns for clarity
		trend_opportunity.columns = ['category', 'avg_quantity_sold', 'avg_frequency']

		# Convert to JSON
		json_data = trend_opportunity.to_json(orient='records', indent=4)

		return json_data

	@staticmethod
	def keywords():
		# Tokenization function
		def tokenize(query):
			query = query.lower()
			tokens = re.findall(r'\b[a-z]+\b', query)  # Extract words only
			return tokens

		# Apply tokenization
		search_df['tokens'] = search_df['query'].apply(tokenize)

		# Group tokens by category (fashion domain mapping)
		fashion_groups = defaultdict(list)

		# Example manual category mapping
		category_keywords = {
			'tank top': ['tank', 'top', 'sleeveless'],
			'trench coat': ['trench', 'coat'],
			'romper': ['romper', 'jumpsuit'],
			'sandals': ['sandals'],
			'denim': ['denim'],
			'summer': ['summer'],
			'winter': ['winter'],
		}

		# Map tokens to categories
		for _, row in search_df.iterrows():
			tokens = row['tokens']
			for cat, keywords in category_keywords.items():
				if any(token in tokens for token in keywords):
					fashion_groups[cat].append(' '.join(tokens))

		# Calculate the count for each category
		top_trends = {cat: len(words) for cat, words in fashion_groups.items()}

		# Convert to DataFrame
		trends_df = pd.DataFrame(list(top_trends.items()), columns=['Keyword', 'SearchCount'])
		trends_df = trends_df.sort_values(by='SearchCount', ascending=False)

		# Limit to top 20
		top_20_df = trends_df.head(20)

		# Convert to JSON
		json_data = top_20_df.to_json(orient='records', indent=4)

		return json_data
