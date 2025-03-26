import pandas as pd
from ast import literal_eval
import spacy
import re
import ast

class IncidentResolver:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.resolution_rules = self._create_resolution_rules()
        
    def _create_resolution_rules(self):
        return {
            'hardware': {
                'patterns': [r'raid', r'controller', r'power supply', r'sensor'],
                'resolution': 'Hardware replacement and redundancy implementation'
            },
            'network': {
                'patterns': [r'bgp', r'dns', r'mpls', r'vpn'],
                'resolution': 'Network configuration audit and protocol optimization'
            },
            'security': {
                'patterns': [r'phishing', r'ransomware', r'malware', r'brute force'],
                'resolution': 'Security patch deployment and monitoring enhancement'
            },
            'database': {
                'patterns': [r'sql', r'replication', r'shard', r'deadlock'],
                'resolution': 'Query optimization and cluster rebalancing'
            },
            'cloud': {
                'patterns': [r'aws', r'azure', r'gcp', r'kubernetes'],
                'resolution': 'Cloud resource optimization and failover strategy'
            },
            'default': 'Root cause analysis and system remediation'
        }

    def _generate_resolution(self, text, tech_components):
        doc = self.nlp(text.lower())
        components = ' '.join(tech_components).lower()
        
        # Check tech components first
        if any(p in components for p in ['aws', 'azure', 'gcp']):
            return "Cloud infrastructure optimization with provider support"
            
        # Pattern matching with priority
        for category, rules in self.resolution_rules.items():
            if category == 'default':
                continue
            if any(re.search(pattern, text.lower()) for pattern in rules['patterns']):
                return rules['resolution']
                
        return self.resolution_rules['default']

    def _determine_status(self, resolution_time):
        return "Resolved" if resolution_time > 0 else "Pending"

    def process_incidents(self, input_path, output_path):
        df = pd.read_excel(input_path)
        #df = df.map(lambda x: str(x).replace('None', '[]'))
        df["NLP_Insights"] = df["NLP_Insights"].fillna("None").replace("nan", "None")
        df["Tech_Components"] = df["Tech_Components"].fillna("None").replace("nan", "None")
        
        # Convert string lists to actual lists
        df['NLP_Insights'] = df['NLP_Insights'].apply(literal_eval)
        df['Tech_Components'] = df['Tech_Components'].apply(literal_eval)
        
        df["NLP_Insights"] = df["NLP_Insights"].fillna("[]").replace("None", "[]")
        df["Tech_Components"] = df["Tech_Components"].fillna("[]").replace("None", "[]")
        # Generate new columns
        df['Status'] = df['ResolutionTime(min)'].apply(self._determine_status)
        df['Resolution'] = df.apply(
            lambda x: self._generate_resolution(x['RootCause'], x['Tech_Components']), 
            axis=1
        )
        df["NLP_Insights"] = df["NLP_Insights"].fillna("None").replace("nan", "None")
        df["Tech_Components"] = df["Tech_Components"].fillna("None").replace("nan", "None")
        # Save enhanced data
        df.to_excel(output_path, index=False)
        return df

# Usage example
resolver = IncidentResolver()
resolver.process_incidents(
    input_path="tickets.xlsx",
    output_path="tickets_resolved.xlsx"
)