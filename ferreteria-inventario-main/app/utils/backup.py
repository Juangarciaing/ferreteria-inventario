"""
Sistema de backup automático
"""
import os
import shutil
import zipfile
import json
from datetime import datetime, timedelta
from flask import current_app
from app import db
from app.models import Usuario, Producto, Categoria, Venta, DetalleVenta, Compra, Proveedor
from app.models.auditoria import AuditoriaLog
import logging

logger = logging.getLogger(__name__)

class BackupManager:
    """Gestor de backups"""
    
    def __init__(self, backup_dir='backups'):
        self.backup_dir = backup_dir
        self.ensure_backup_dir()
    
    def ensure_backup_dir(self):
        """Asegurar que el directorio de backup existe"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            logger.info(f"Directorio de backup creado: {self.backup_dir}")
    
    def create_database_backup(self, include_audit_logs=True):
        """Crear backup de la base de datos"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"database_backup_{timestamp}.json"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Obtener datos de todas las tablas
            backup_data = {
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0',
                'tables': {}
            }
            
            # Backup de usuarios
            usuarios = Usuario.query.all()
            backup_data['tables']['usuarios'] = [usuario.to_dict() for usuario in usuarios]
            
            # Backup de categorías
            categorias = Categoria.query.all()
            backup_data['tables']['categorias'] = [categoria.to_dict() for categoria in categorias]
            
            # Backup de proveedores
            proveedores = Proveedor.query.all()
            backup_data['tables']['proveedores'] = [proveedor.to_dict() for proveedor in proveedores]
            
            # Backup de productos
            productos = Producto.query.all()
            backup_data['tables']['productos'] = [producto.to_dict() for producto in productos]
            
            # Backup de ventas
            ventas = Venta.query.all()
            backup_data['tables']['ventas'] = [venta.to_dict() for venta in ventas]
            
            # Backup de detalles de venta
            detalles_venta = DetalleVenta.query.all()
            backup_data['tables']['detalles_venta'] = [detalle.to_dict() for detalle in detalles_venta]
            
            # Backup de compras
            compras = Compra.query.all()
            backup_data['tables']['compras'] = [compra.to_dict() for compra in compras]
            
            # Backup de logs de auditoría (opcional)
            if include_audit_logs:
                audit_logs = AuditoriaLog.query.all()
                backup_data['tables']['auditoria_logs'] = [log.to_dict() for log in audit_logs]
            
            # Guardar backup
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Backup de base de datos creado: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Error creando backup de base de datos: {e}")
            raise
    
    def create_full_backup(self, include_files=True):
        """Crear backup completo del sistema"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"full_backup_{timestamp}.zip"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Backup de base de datos
                db_backup_path = self.create_database_backup()
                zipf.write(db_backup_path, os.path.basename(db_backup_path))
                
                # Backup de archivos de configuración
                config_files = [
                    'app/config.py',
                    'requirements.txt',
                    'run_api.py',
                    'init_db.py'
                ]
                
                for config_file in config_files:
                    if os.path.exists(config_file):
                        zipf.write(config_file, f"config/{os.path.basename(config_file)}")
                
                # Backup de archivos de la aplicación
                if include_files:
                    app_files = [
                        'app/__init__.py',
                        'app/api_routes.py',
                        'app/api_additional.py',
                        'app/api_auditoria.py',
                        'app/api_export.py',
                        'app/api_monitoring.py',
                        'app/api_docs.py'
                    ]
                    
                    for app_file in app_files:
                        if os.path.exists(app_file):
                            zipf.write(app_file, f"app/{os.path.basename(app_file)}")
                
                # Información del backup
                backup_info = {
                    'timestamp': datetime.now().isoformat(),
                    'version': '1.0.0',
                    'type': 'full_backup',
                    'includes': {
                        'database': True,
                        'config_files': True,
                        'app_files': include_files,
                        'audit_logs': True
                    }
                }
                
                zipf.writestr('backup_info.json', json.dumps(backup_info, indent=2))
            
            logger.info(f"Backup completo creado: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Error creando backup completo: {e}")
            raise
    
    def restore_database_backup(self, backup_path):
        """Restaurar backup de base de datos"""
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Limpiar tablas existentes
            db.session.query(DetalleVenta).delete()
            db.session.query(Venta).delete()
            db.session.query(Compra).delete()
            db.session.query(Producto).delete()
            db.session.query(Proveedor).delete()
            db.session.query(Categoria).delete()
            db.session.query(Usuario).delete()
            db.session.query(AuditoriaLog).delete()
            
            # Restaurar datos
            tables = backup_data.get('tables', {})
            
            # Restaurar usuarios
            if 'usuarios' in tables:
                for user_data in tables['usuarios']:
                    usuario = Usuario(
                        nombre=user_data['nombre'],
                        email=user_data['email'],
                        rol=user_data['rol'],
                        telefono=user_data.get('telefono'),
                        direccion=user_data.get('direccion')
                    )
                    usuario.password_hash = user_data.get('password_hash')
                    db.session.add(usuario)
            
            # Restaurar categorías
            if 'categorias' in tables:
                for cat_data in tables['categorias']:
                    categoria = Categoria(nombre=cat_data['nombre'])
                    db.session.add(categoria)
            
            # Restaurar proveedores
            if 'proveedores' in tables:
                for prov_data in tables['proveedores']:
                    proveedor = Proveedor(**prov_data)
                    db.session.add(proveedor)
            
            # Restaurar productos
            if 'productos' in tables:
                for prod_data in tables['productos']:
                    producto = Producto(**prod_data)
                    db.session.add(producto)
            
            # Restaurar ventas
            if 'ventas' in tables:
                for venta_data in tables['ventas']:
                    venta = Venta(**venta_data)
                    db.session.add(venta)
            
            # Restaurar detalles de venta
            if 'detalles_venta' in tables:
                for detalle_data in tables['detalles_venta']:
                    detalle = DetalleVenta(**detalle_data)
                    db.session.add(detalle)
            
            # Restaurar compras
            if 'compras' in tables:
                for compra_data in tables['compras']:
                    compra = Compra(**compra_data)
                    db.session.add(compra)
            
            # Restaurar logs de auditoría
            if 'auditoria_logs' in tables:
                for log_data in tables['auditoria_logs']:
                    log = AuditoriaLog(**log_data)
                    db.session.add(log)
            
            db.session.commit()
            logger.info(f"Backup restaurado exitosamente: {backup_path}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error restaurando backup: {e}")
            raise
    
    def list_backups(self):
        """Listar backups disponibles"""
        try:
            backups = []
            for filename in os.listdir(self.backup_dir):
                if filename.endswith('.json') or filename.endswith('.zip'):
                    file_path = os.path.join(self.backup_dir, filename)
                    stat = os.stat(file_path)
                    backups.append({
                        'filename': filename,
                        'path': file_path,
                        'size': stat.st_size,
                        'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'type': 'database' if filename.endswith('.json') else 'full'
                    })
            
            # Ordenar por fecha de creación (más reciente primero)
            backups.sort(key=lambda x: x['created'], reverse=True)
            return backups
            
        except Exception as e:
            logger.error(f"Error listando backups: {e}")
            return []
    
    def cleanup_old_backups(self, days_to_keep=30):
        """Limpiar backups antiguos"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            deleted_count = 0
            
            for filename in os.listdir(self.backup_dir):
                if filename.endswith('.json') or filename.endswith('.zip'):
                    file_path = os.path.join(self.backup_dir, filename)
                    stat = os.stat(file_path)
                    file_date = datetime.fromtimestamp(stat.st_ctime)
                    
                    if file_date < cutoff_date:
                        os.remove(file_path)
                        deleted_count += 1
                        logger.info(f"Backup antiguo eliminado: {filename}")
            
            logger.info(f"Se eliminaron {deleted_count} backups antiguos")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error limpiando backups antiguos: {e}")
            return 0
    
    def get_backup_stats(self):
        """Obtener estadísticas de backups"""
        try:
            backups = self.list_backups()
            total_size = sum(backup['size'] for backup in backups)
            
            return {
                'total_backups': len(backups),
                'total_size': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'database_backups': len([b for b in backups if b['type'] == 'database']),
                'full_backups': len([b for b in backups if b['type'] == 'full']),
                'oldest_backup': backups[-1]['created'] if backups else None,
                'newest_backup': backups[0]['created'] if backups else None
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de backup: {e}")
            return {}

# Instancia global del gestor de backup
backup_manager = BackupManager()

def schedule_automatic_backup():
    """Programar backup automático"""
    try:
        # Crear backup diario
        backup_path = backup_manager.create_database_backup()
        logger.info(f"Backup automático creado: {backup_path}")
        
        # Limpiar backups antiguos
        backup_manager.cleanup_old_backups()
        
        return backup_path
        
    except Exception as e:
        logger.error(f"Error en backup automático: {e}")
        return None
