import click
import os
from pathlib import Path
from configparser import ConfigParser

# 환경 매핑 딕셔너리 추가
ENV_MAPPING = {
    'development': 'development',
    'dev': 'development',
    'test': 'test',
    'production': 'production',
    'prod': 'production'
}


@click.group()
def cli():
    pass


@cli.command()
@click.option('--env', default='development', help='Environment (development/test/production)')
def init(env):
    """특정 환경의 데이터베이스 초기화"""
    # 환경 이름 정규화
    env = ENV_MAPPING.get(env.lower(), 'development')

    # 환경 설정 로드
    config = ConfigParser()
    config_path = Path('alembic.ini')
    if not config_path.exists():
        raise click.ClickException("alembic.ini file not found!")

    config.read('alembic.ini')

    # 환경별 DB URL 설정
    try:
        db_url = config.get(env, 'sqlalchemy.url')
        os.environ['DATABASE_URL'] = db_url
    except Exception as e:
        raise click.ClickException(f"Error reading database configuration for environment '{env}': {str(e)}")

    # DB 초기화 스크립트 실행
    try:
        from scripts.db_reset import reset_database
        reset_database(os.environ['DATABASE_URL'])
        click.echo(f"{env} database initialized successfully!")
    except Exception as e:
        raise click.ClickException(f"Error initializing database: {str(e)}")


@cli.command()
@click.option('--env', default='development', help='Environment (development/test/production)')
@click.option('--sample', is_flag=True, help='Include sample data')
def setup(env, sample):
    """데이터베이스 설정 및 샘플 데이터 로드"""
    # DB 초기화
    init(env)

    if sample:
        try:
            from scripts.load_sample_data import load_samples
            load_samples(os.environ['DATABASE_URL'])
            click.echo("Sample data loaded successfully!")
        except Exception as e:
            raise click.ClickException(f"Error loading sample data: {str(e)}")


@cli.command()
def show_config():
    """현재 설정 표시"""
    config = ConfigParser()
    config.read('alembic.ini')

    click.echo("Available environments:")
    for section in config.sections():
        if section in ['development', 'test', 'production']:
            click.echo(f"  {section}:")
            click.echo(f"    URL: {config.get(section, 'sqlalchemy.url')}")


if __name__ == '__main__':
    cli()