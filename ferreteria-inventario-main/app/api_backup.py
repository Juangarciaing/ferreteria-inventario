"""
Endpoints para gestión de backups
"""
from flask import Blueprint, request, jsonify, send_from_directory
from app.api_routes import token_required, rol_requerido
from app.utils.backup import backup_manager
from datetime import datetime
from werkzeug.utils import secure_filename
import os

backup_api = Blueprint('backup_api', __name__, url_prefix='/api')

@backup_api.route('/backup/create', methods=['POST'])
@token_required
@rol_requerido('admin')
def create_backup(current_user):
    """Crear backup de la base de datos (solo admin)"""
    try:
        backup_type = request.json.get('type', 'database')  # 'database' o 'full'
        include_audit_logs = request.json.get('include_audit_logs', True)
        include_files = request.json.get('include_files', True)
        
        if backup_type == 'full':
            backup_path = backup_manager.create_full_backup(include_files=include_files)
        else:
            backup_path = backup_manager.create_database_backup(include_audit_logs=include_audit_logs)
        
        return jsonify({
            'message': 'Backup creado exitosamente',
            'backup_path': backup_path,
            'type': backup_type,
            'timestamp': datetime.now().isoformat()
        }), 201
        
    except Exception as e:
        return jsonify({'message': 'Error creando backup', 'detail': str(e)}), 500

@backup_api.route('/backup/list', methods=['GET'])
@token_required
@rol_requerido('admin')
def list_backups(current_user):
    """Listar backups disponibles (solo admin)"""
    try:
        backups = backup_manager.list_backups()
        stats = backup_manager.get_backup_stats()
        
        return jsonify({
            'backups': backups,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Error listando backups', 'detail': str(e)}), 500

@backup_api.route('/backup/download/<path:filename>', methods=['GET'])
@token_required
@rol_requerido('admin')
def download_backup(current_user, filename):
    """Descargar backup (solo admin)"""
    try:
        # Sanitizar nombre de archivo para prevenir path traversal
        safe_filename = secure_filename(filename)
        
        # Validar que el archivo existe en el directorio de backups
        backup_path = os.path.join(backup_manager.backup_dir, safe_filename)
        
        if not os.path.exists(backup_path):
            return jsonify({'message': 'Backup no encontrado'}), 404
        
        # Usar send_from_directory para prevenir path traversal
        return send_from_directory(
            backup_manager.backup_dir,
            safe_filename,
            as_attachment=True,
            download_name=safe_filename,
            mimetype='application/octet-stream'
        )
        
    except Exception as e:
        return jsonify({'message': 'Error descargando backup', 'detail': str(e)}), 500

@backup_api.route('/backup/restore', methods=['POST'])
@token_required
@rol_requerido('admin')
def restore_backup(current_user):
    """Restaurar backup (solo admin)"""
    try:
        backup_filename = request.json.get('filename')
        if not backup_filename:
            return jsonify({'message': 'Nombre de archivo de backup requerido'}), 400
        
        # Sanitizar nombre de archivo para prevenir path traversal
        safe_filename = secure_filename(backup_filename)
        
        # Validar extensión del archivo
        if not safe_filename.endswith(('.sql', '.gz', '.zip', '.bak')):
            return jsonify({'message': 'Formato de archivo de backup no válido'}), 400
        
        backup_path = os.path.join(backup_manager.backup_dir, safe_filename)
        
        if not os.path.exists(backup_path):
            return jsonify({'message': 'Backup no encontrado'}), 404
        
        # Validar que el archivo está dentro del directorio de backups
        real_backup_path = os.path.realpath(backup_path)
        real_backup_dir = os.path.realpath(backup_manager.backup_dir)
        
        if not real_backup_path.startswith(real_backup_dir):
            return jsonify({'message': 'Acceso denegado'}), 403
        
        # Restaurar backup
        success = backup_manager.restore_database_backup(backup_path)
        
        if success:
            return jsonify({
                'message': 'Backup restaurado exitosamente',
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({'message': 'Error restaurando backup'}), 500
        
    except Exception as e:
        return jsonify({'message': 'Error restaurando backup', 'detail': str(e)}), 500

@backup_api.route('/backup/cleanup', methods=['POST'])
@token_required
@rol_requerido('admin')
def cleanup_backups(current_user):
    """Limpiar backups antiguos (solo admin)"""
    try:
        days_to_keep = request.json.get('days_to_keep', 30)
        deleted_count = backup_manager.cleanup_old_backups(days_to_keep)
        
        return jsonify({
            'message': f'Se eliminaron {deleted_count} backups antiguos',
            'deleted_count': deleted_count,
            'days_to_keep': days_to_keep,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Error limpiando backups', 'detail': str(e)}), 500

@backup_api.route('/backup/stats', methods=['GET'])
@token_required
@rol_requerido('admin')
def get_backup_stats(current_user):
    """Obtener estadísticas de backups (solo admin)"""
    try:
        stats = backup_manager.get_backup_stats()
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'message': 'Error obteniendo estadísticas', 'detail': str(e)}), 500

@backup_api.route('/backup/schedule', methods=['POST'])
@token_required
@rol_requerido('admin')
def schedule_backup(current_user):
    """Programar backup automático (solo admin)"""
    try:
        schedule_config = request.json.get('schedule', {})
        
        # Aquí se implementaría la lógica de programación
        # Por ahora, solo creamos un backup inmediato
        backup_path = backup_manager.create_database_backup()
        
        return jsonify({
            'message': 'Backup programado exitosamente',
            'backup_path': backup_path,
            'schedule': schedule_config,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Error programando backup', 'detail': str(e)}), 500
