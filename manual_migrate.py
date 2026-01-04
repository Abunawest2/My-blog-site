import os
import MySQLdb
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database credentials from environment variables
DB_NAME = os.environ.get('DATABASE_NAME')
DB_USER = os.environ.get('DATABASE_USER')
DB_PASSWORD = os.environ.get('DATABASE_PASSWORD')
DB_HOST = os.environ.get('DATABASE_HOST')
DB_PORT = int(os.environ.get('DATABASE_PORT', 3306))

# SQL statements to execute
SQL_STATEMENTS = """
ALTER TABLE `firstblog_category` ADD COLUMN `is_active` bool DEFAULT b'1' NOT NULL;
ALTER TABLE `firstblog_category` ALTER COLUMN `is_active` DROP DEFAULT;
ALTER TABLE `firstblog_category` ADD COLUMN `level` integer UNSIGNED DEFAULT 3 NOT NULL CHECK (`level` >= 0);
ALTER TABLE `firstblog_category` ALTER COLUMN `level` DROP DEFAULT;
ALTER TABLE `firstblog_category` ADD COLUMN `parent_id` bigint NULL;
ALTER TABLE `firstblog_category` ADD CONSTRAINT `firstblog_category_parent_id_622f14dc_fk_firstblog_category_id` FOREIGN KEY (`parent_id`) REFERENCES `firstblog_category`(`id`);
ALTER TABLE `firstblog_category` ADD COLUMN `slug` varchar(100) DEFAULT '' NOT NULL;
ALTER TABLE `firstblog_category` ALTER COLUMN `slug` DROP DEFAULT;
ALTER TABLE `firstblog_category` ADD COLUMN `super_category` varchar(20) NULL;
ALTER TABLE `firstblog_category` ADD CONSTRAINT `unique_category_per_genre` UNIQUE (`name`, `super_category`);
ALTER TABLE `firstblog_category` ADD CONSTRAINT `unique_child_category` UNIQUE (`name`, `parent_id`);
CREATE INDEX `firstblog_category_slug_1dd859ba` ON `firstblog_category` (`slug`);
"""

def manual_migrate():
    """Connects to the database and executes the SQL statements."""
    try:
        # Connect to the database
        db = MySQLdb.connect(
            host=DB_HOST,
            user=DB_USER,
            passwd=DB_PASSWORD,
            db=DB_NAME,
            port=DB_PORT
        )
        
        # Create a cursor
        cursor = db.cursor()
        
        # Execute the SQL statements
        for statement in SQL_STATEMENTS.split(';'):
            if statement.strip():
                try:
                    cursor.execute(statement)
                    print(f"Successfully executed: {statement.strip()}")
                except MySQLdb.OperationalError as e:
                    # Ignore errors for columns/constraints that already exist
                    if e.args[0] in (1060, 1061, 1091): # Duplicate column, Duplicate key, Can't DROP
                        print(f"Ignoring error (already exists?): {e}")
                    else:
                        raise e

        # Commit the changes
        db.commit()
        
        print("\nManual migration completed successfully!")
        
    except MySQLdb.Error as e:
        print(f"\nDatabase error: {e}")
        
    finally:
        # Close the connection
        if 'db' in locals() and db.open:
            db.close()

if __name__ == "__main__":
    manual_migrate()
